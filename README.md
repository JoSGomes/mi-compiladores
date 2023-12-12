# mi-compiladores
Repositório dedicado a disciplina  MI - Processadores de Linguagem de Programação para a criação de um Analisador Léxico



# Analisador Léxico

O Analisador Léxico foi criado utilizado o alfabeto disponível no Problema 1 da disciplina, a partir dele foi escolhido a ideia de autômatos finitos como princípio base. Entretanto, a solução não abrange completamente a ideia, apenas o conceito de estados. 
No arquivo `lexical_analizer.py` está descrito no analisador e os seus estados estão definidos e comentados após a criação de cada um deles, **é de suma importância que se leia o comentário logo após o estado para melhor entendimento do funcionamento**.


# Analisador Sintático

O analizador foi criado utilizando a gramática disponível no repositório em `./grammar`. A teoria aplicada foi do Analisador Descendente Recursivo. 


# Execução

Para executar siga as seguintes instruções:

- Sobre as entradas:
  - Como pedido no Problema 1, as `n` entradas devem estar dispostas no arquivo antes da execução;
  - Para analisar as entradas, basta executar o arquivo `main.py`;
- Sobre as saídas:
  - As saídas estarão nomeadas com o nome do `<nome_arquivo_de_entrada> + "_saida.txt"`
- Caso esteja executando em Linux, é possível que tenha que ajustar o caminho relativo para pasta `files` no arquivo `main.py`, na variável global `PATH_FILES`, além dos `/` na abertura dos arquivos de entrada e saída no laço `for` no analisador léxico;

# Logs

Caso queira verificar com mais detalhes a execução, consulte os `logs` que estão sendo salvos no arquivo `sintax_analizer.log`. Nele é possível verificar a cadeia de execução, assim como todos os erros associados.

## Condições de desenvolvimento
- SO: Windows 10
- Linguagem: Python 3.11.4
