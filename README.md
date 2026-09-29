# Mythology in Art

**How has Greek mythology been represented in art over time?** Um projeto de Flaviana Gomes que une pesquisa visual, APIs de museus, análise de dados e uma interface exploratória.

## Estado do projeto

Esta primeira versão apresenta uma **amostra curada de cinco obras reais do Metropolitan Museum of Art**. A página `index.html` abre diretamente no navegador e permite filtrar personagem e período. Contagens da página descrevem somente essa amostra; não medem a frequência da mitologia em acervos ou épocas. Cada obra liga à ficha original. As imagens abertas via Met podem exigir internet.

O script `src/coletar.py` oferece a próxima etapa reproduzível: busca programática nas APIs do Met e do Art Institute of Chicago, normalização em CSV e SQLite, e consultas SQL. Ele depende de acesso à internet e **não foi executado neste ambiente**, onde os domínios das APIs não estavam acessíveis. A seleção automática por palavra-chave pode incluir obras irrelevantes: é preciso revisão manual antes de analisar frequência por personagem ou época.

## Pergunta e método

- Unidade de análise: obra, identificada por museu e ID.
- Variáveis: título, artista/cultura, data textual e numérica quando disponível, material, classificação, personagem pesquisado, fonte e licença de imagem.
- A busca por `Athena`, `Zeus`, `Aphrodite`, `Apollo`, `Herakles`, `Medusa` e variantes encontra **candidatos**, não uma classificação definitiva de iconografia.
- Um personagem pode aparecer em várias consultas. Duplicamos a associação obra-personagem no relacionamento, não a obra no catálogo.
- Datas aproximadas, arte greco-romana de períodos posteriores, transliterações e ausência de imagens precisam de tratamento explícito.
- Perguntas futuras: mudanças de materiais e tipos de obra por período; redes personagem–narrativa–artista; comparação de cobertura entre instituições. Não há inferência de tendência histórica a partir de resultados de busca sem auditar seleção e cobertura.

## Executar

Abra `index.html` diretamente. Para criar um catálogo maior com acesso às APIs:

```bash
python src/coletar.py --max-por-termo 20 --saida dados
```

O comando grava `dados/obras.csv`, `dados/associacoes.csv` e `dados/mythology.sqlite`. Veja consultas em `sql/analises.sql`. Python 3.10+ e biblioteca padrão; nenhum token é necessário. O coletor espera entre chamadas ao Met e usa a versão paginada `/v1.1/search`.

## Fontes e atribuição

- [The Met Collection API](https://metmuseum.github.io/) e fichas originais ligadas em cada cartão. Metadados e imagens desta seleção estão marcados como domínio público nas fichas; confira cada item antes de reutilizar em outra publicação.
- [Art Institute of Chicago API](https://api.artic.edu/docs/). O coletor usa apenas registros `is_public_domain=true` e imagens IIIF quando disponíveis.

Não há dados sintéticos apresentados como obras reais, modelos de IA treinados ou dashboard Power BI nesta versão. A construção do conjunto completo, análise exploratória e dashboard são as próximas entregas.
