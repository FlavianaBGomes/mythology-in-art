-- Execute após python src/coletar.py; SQLite.
-- Resultado bruto de busca é candidato, sujeito a revisão curatorial.
SELECT personagem, COUNT(DISTINCT museu || ':' || obra_id) AS obras_candidatas
FROM associacoes GROUP BY personagem ORDER BY obras_candidatas DESC;

SELECT museu, classificacao, COUNT(*) AS obras
FROM obras GROUP BY museu, classificacao ORDER BY obras DESC;

-- Ano é aproximado e só deve ser usado se a fonte o informar.
SELECT personagem, CAST(CAST(ano_inicio AS INTEGER) / 100 AS INTEGER) * 100 AS seculo_aproximado,
       COUNT(DISTINCT obras.museu || ':' || obras.obra_id) AS obras
FROM obras JOIN associacoes USING (museu, obra_id)
WHERE ano_inicio IS NOT NULL
GROUP BY personagem, seculo_aproximado ORDER BY personagem, seculo_aproximado;
