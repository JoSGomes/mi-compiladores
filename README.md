# mi-compiladores
Repositório dedicado a disciplina  MI - Processadores de Linguagem de Programação para a criação de um Analisador Léxico


# Analisador Léxico

O Analisador Léxico foi criado utilizado o alfabeto disponível no Problema 1 da disciplina, a partir dele foi escolhido a ideia de autômatos finitos como princípio base. Entretanto, a solução não abrange completamente a ideia, apenas o conceito de estados. 
No arquivo `lexical_analizer.py` está descrito no analisador e os seus estados estão definidos e comentados após a criação de cada um deles, **é de suma importância que se leia o comentário logo após o estado para melhor entendimento do funcionamento**.


# Analisador Sintático

O Analizador Sinático foi criado utilizando a gramática disponível no repositório em `./grammar`. A teoria aplicada foi do Analisador Descendente Recursivo. 

# Analisador Semântico

O Analizador Semântico foi criado baseado nas regras definidas nas Sessões PBL e estão entremeadas ao Sintático. Os escopos global, classe, método e herança estão relacionados por endereço de memória.

# Execução

Para executar siga as seguintes instruções:

- Sobre as entradas:
  - Como pedido no Problema 1, as `n` entradas devem estar dispostas no arquivo antes da execução;
  - Para analisar as entradas, basta executar o arquivo `main.py`;
- Sobre as saídas:
  - As saídas estarão nomeadas com o nome do `<nome_arquivo_de_entrada> + "_saida.txt"`
- Caso esteja executando em Linux, é possível que tenha que ajustar o caminho relativo para pasta `files` no arquivo `main.py`, na variável global `PATH_FILES`, além dos `/` na abertura dos arquivos de entrada e saída no laço `for` no analisador léxico;

- Obs.: Existem dois arquivo chamados `sintax_analizer.py` e `sintax_semantic_analizer.py`, a `main.py`, a qual será executada sempre, está configurada para utilizar o os três analizadores. Caso queira executar somente o sintático, terá que muda a classe que está sendo instanciada para a classe que existe em `sintax_analizer.py` na `main.py`.

# Logs

Caso queira verificar com mais detalhes a execução, consulte os `logs` que estão sendo salvos no arquivo `sintax_analizer.log` e `semantic_analizer.log`. Neles é possível verificar a cadeia de execução (sintático), assim como todos os erros associados.

## Condições de desenvolvimento
- SO: Windows 10
- Linguagem: Python 3.11.4
