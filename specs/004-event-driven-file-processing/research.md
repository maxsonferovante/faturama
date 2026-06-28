# Research: Processamento Assincrono de Faturas por Eventos

## Decision 1: SQS acionará a Step Function por EventBridge Pipe

**Decision**: O caminho oficial entre a fila SQS e a Step Function será `SQS -> EventBridge Pipe -> Step Functions`, sem adicionar Lambda ou poller customizado para iniciar execuções.

**Rationale**: A documentação oficial do SQS posiciona EventBridge Pipes como integração ponto a ponto escalável entre uma fila SQS e serviços AWS, incluindo Step Functions. Isso atende ao requisito de manter o bucket desacoplado da execução do worker sem criar um componente extra apenas para traduzir mensagens.

**Alternatives considered**:

- **Consumidor customizado em Python lendo SQS**: descartado porque adiciona um processo permanente para uma responsabilidade que a plataforma já cobre.
- **Lambda entre SQS e Step Functions**: descartado porque aumenta superfícies operacionais e custo conceitual sem necessidade funcional na v1.
- **Step Function iniciada diretamente por evento de bucket**: descartado porque perderia o desacoplamento explícito exigido pela arquitetura alvo.

## Decision 2: A Step Function será Standard e usará `ecs:runTask` no padrão Request Response

**Decision**: A orquestração usará uma Step Function Standard com um estado de preparação do payload seguido de `arn:aws:states:::ecs:runTask` sem o sufixo `.sync`, de forma que a execução apenas dispare a task ECS e termine após registrar o dispatch.

**Rationale**: A documentação do Step Functions distingue `Request Response` de `.sync` e mostra que, sem o sufixo `.sync`, o workflow avança após a chamada HTTP/API retornar, sem monitorar a conclusão do job. Isso coincide exatamente com o requisito de disparo assíncrono. A escolha por Standard, e não Express, privilegia trilha de execução mais auditável e depuração operacional mais simples para uma v1 orientada a confiabilidade.

**Alternatives considered**:

- **Usar `.sync`**: descartado porque faria a Step Function esperar a task ECS terminar, contrariando RT-006.
- **Usar `.waitForTaskToken`**: descartado porque exigiria callback explícito e mais acoplamento entre container e Step Functions sem valor adicional nesta v1.
- **Usar Express Workflow**: descartado porque o ganho de throughput não supera a perda de histórico operacional detalhado para o primeiro corte.

## Decision 3: O contrato canônico será normalizado na borda da Step Function

**Decision**: O evento bruto vindo do S3 via SQS será tratado como envelope de transporte, e a Step Function produzirá um `ProcessingCommand` canônico com `bucket`, `object_key`, `event_time`, `processing_id`, `source` e `metadata`, que será então passado ao worker ECS. O `processing_id` identificará apenas a tentativa operacional; a identidade canônica do documento continuará sendo derivada do hash do PDF calculado no worker.

**Rationale**: O evento nativo do S3 não inclui um `processing_id` de domínio e carrega uma estrutura voltada a notificações, não a processamento interno. Normalizar na Step Function permite fixar um contrato estável para a aplicação enquanto preserva o evento bruto apenas como evidência de origem. O `processing_id` pode ser derivado do identificador da execução da Step Function, garantindo unicidade por tentativa sem competir com a regra canônica de deduplicação por hash do conteúdo.

**Alternatives considered**:

- **Usar o JSON bruto do S3 dentro do container**: descartado porque acopla o worker ao formato de notificação e dificulta versionamento do contrato.
- **Gerar `processing_id` no S3/SQS**: descartado porque esses serviços não oferecem esse enriquecimento de domínio de forma nativa para este fluxo.
- **Persistir somente `messageId` da SQS como identificador principal**: descartado porque ele descreve transporte, não a execução lógica do processamento.
- **Usar `processing_id` como identidade canônica do documento**: descartado porque retries e reuploads legítimos produziriam novas tentativas para o mesmo arquivo.

## Decision 4: A entrada externa usará URL assinada temporária para `PUT` no bucket de entrada

**Decision**: A v1 aceitará uploads externos por URL assinada temporária para `PUT` em chaves pré-autorizadas do bucket `pre-processamento-faturama`, com rastreabilidade do grant que originou o upload.

**Rationale**: A documentação oficial do S3 afirma que URLs assinadas permitem upload sem distribuir credenciais AWS ao cliente e que o upload herda as permissões de quem gera a URL. Isso atende à exigência de entrada externa controlada, minimiza a exposição de credenciais permanentes e mantém o bucket sob propriedade do ambiente processador após a gravação.

**Alternatives considered**:

- **Credenciais permanentes por integrador**: descartado porque amplia superfície de segredo e governança.
- **Upload apenas por sistemas internos com IAM**: descartado porque não atende à decisão de abrir a entrada externa já na v1.
- **Proxy síncrono de upload através do worker**: descartado porque reintroduz acoplamento e bloqueio em um fluxo que deve começar assíncrono.

## Decision 5: O bucket de entrada continuará único, mas com filtros de evento e prefixos operacionais

**Decision**: O bucket `pre-processamento-faturama` continuará sendo o ponto de entrada da v1, porém as notificações serão filtradas para PDFs de entrada e o runtime usará prefixos separados para arquivos recebidos, artefatos e saídas duráveis.

**Rationale**: A documentação do S3 alerta para loops quando o mesmo bucket recebe gravações produzidas pelo próprio fluxo acionado por evento. Prefixos e filtros por sufixo `.pdf` mantêm a simplicidade de um bucket único sem reacionar artefatos ou resultados escritos pelo worker. Além disso, a documentação oficial informa que notificações S3 não suportam fila FIFO diretamente, o que reforça a adoção de uma fila SQS standard para este desenho.

**Alternatives considered**:

- **Dois buckets separados desde a v1**: descartado porque adiciona governança extra antes de existir necessidade real.
- **Sem filtros de evento**: descartado porque abre risco direto de loop operacional.
- **Fila FIFO ligada diretamente ao S3**: descartado porque não é suportado pelo mecanismo nativo de notificação do S3.

## Decision 6: O worker ECS reaproveitará o `process_invoice` atual atrás de um novo entrypoint assíncrono

**Decision**: A imagem Docker hospedará um entrypoint de worker que recebe o contrato normalizado, baixa o PDF do S3 para armazenamento efêmero, carrega configurações de ambiente e delega o processamento ao use case `process_invoice`, encapsulando apenas as adaptações externas necessárias.

**Rationale**: O repositório já possui um pipeline funcional e coberto por testes para extração, orquestração e persistência. Reaproveitá-lo reduz risco de regressão e mantém o esforço concentrado na borda assíncrona, não em reescrever o núcleo do produto.

**Alternatives considered**:

- **Reescrever o pipeline inteiro para o modo assíncrono**: descartado porque expande escopo e risco sem necessidade.
- **Executar a CLI atual como shell command opaco dentro do container**: descartado porque enfraquece contratos, observabilidade e testabilidade do novo worker.
- **Montar o PDF por volume compartilhado em vez de baixar do S3**: descartado porque reduz paridade com o ambiente alvo e complica o isolamento por task.

## Decision 7: Estado durável, revisão, checkpoints e manifesto de artefatos irão para PostgreSQL + S3

**Decision**: O ambiente assíncrono persistirá status operacional, fila de revisão, checkpoints resumíveis, manifesto dos artefatos OpenDataLoader e dados canônicos em PostgreSQL, enquanto PDFs e artefatos grandes continuarão em S3. Os arquivos derivados do OpenDataLoader serão gravados em um bucket dedicado chamado `processados-faturama`.

**Rationale**: O modelo atual baseado em SQLite e caminhos locais atende ao fluxo CLI, mas não sobrevive a tasks ECS efêmeras nem a reprocessamento distribuído. PostgreSQL centraliza consistência transacional e consultas operacionais, enquanto S3 preserva objetos e artefatos maiores sem inflar o banco. Separar os artefatos processados em `processados-faturama` simplifica auditoria, avaliação e consulta posterior, além de evitar misturar entrada bruta com saída derivada.

**Alternatives considered**:

- **Continuar com SQLite dentro da task**: descartado porque o disco da task não é uma base durável compartilhada.
- **Persistir tudo em S3**: descartado porque dificulta consultas, status transicional e integridade operacional.
- **Adicionar EFS para manter SQLite**: descartado porque aumenta complexidade e não resolve tão bem a necessidade relacional quanto PostgreSQL.
- **Salvar artefatos derivados no mesmo bucket de entrada**: descartado porque reduz clareza operacional e aumenta risco de confusão entre insumo e saída auditável.

## Decision 8: O estado `REVIEW_REQUIRED` permanecerá pendente e o resultado será descoberto por outra API via banco

**Decision**: Solicitações em revisão permanecerão em `REVIEW_REQUIRED` como estado não terminal, e a descoberta de conclusão, parcialidade ou falha por sistemas consumidores ocorrerá por outra API apoiada no banco de dados persistido, não por evento externo de término emitido pelo worker.

**Rationale**: A decisão reduz acoplamento entre o processador e os consumidores do contexto maior, centraliza a visão oficial do estado em armazenamento durável e evita tratar revisão pendente como sucesso parcial ou erro definitivo. Também simplifica o fluxo assíncrono inicial porque a Step Function só precisa garantir o dispatch e a persistência do ledger.

**Alternatives considered**:

- **Evento externo de conclusão como canal oficial**: descartado porque a clarificação definiu polling por outra API como mecanismo principal.
- **`REVIEW_REQUIRED` como `PARTIAL` terminal**: descartado porque encerraria prematuramente um processo ainda retomável.
- **`REVIEW_REQUIRED` como `FAILED`**: descartado porque revisão operacional não é falha terminal.

## Decision 9: O ambiente local usará Terraform contra o emulador AWS e PostgreSQL compatível em Docker, com diferença documentada para logs

**Decision**: O desenvolvimento local será validado com Terraform apontando para o endpoint AWS emulado, usando os mesmos nomes de recursos e contratos de mensagem do ambiente alvo. O banco será um PostgreSQL compatível em Docker e a paridade de logs será tratada como diferença documentada quando a emulação local não reproduzir integralmente a criação de log groups.

**Rationale**: A verificação local de cobertura confirmou suporte para S3, SQS, Step Functions, EventBridge Pipes, ECS, IAM e RDS via Terraform no ambiente emulado, enquanto a checagem não retornou cobertura para `AWS::Logs::LogGroup`. Isso indica que o fluxo principal pode ser validado localmente sem AWS real, mas a observabilidade precisa de uma nota explícita de paridade em desenvolvimento.

**Alternatives considered**:

- **Usar AWS real em desenvolvimento**: descartado porque viola o requisito de custo e de desenvolvimento local obrigatório.
- **Remover logs centralizados da v1**: descartado porque a constituição do projeto exige observabilidade explícita.
- **Simular o banco com SQLite também no worker local**: descartado porque reduziria a paridade com o ambiente alvo justamente no componente mais sensível da feature.

## Source References

- AWS Step Functions ECS integration: `https://docs.aws.amazon.com/step-functions/latest/dg/connect-ecs.html`
- Step Functions integration patterns: `https://docs.aws.amazon.com/step-functions/latest/dg/connect-to-resource.html`
- Amazon S3 event notifications: `https://docs.aws.amazon.com/AmazonS3/latest/userguide/EventNotifications.html`
- Amazon S3 presigned uploads: `https://docs.aws.amazon.com/AmazonS3/latest/userguide/PresignedUrlUploadObject.html`
- Amazon SQS with EventBridge Pipes: `https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/eb-pipes-integration.html`
- Step Functions triggered by EventBridge: `https://docs.aws.amazon.com/step-functions/latest/dg/eventbridge-integration.html`
- Amazon ECS logs to CloudWatch: `https://docs.aws.amazon.com/AmazonECS/latest/developerguide/using_awslogs.html`
- MiniStack overview: `https://ministack.org/`
