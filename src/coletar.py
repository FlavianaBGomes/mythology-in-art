"""Busca obras candidatas em APIs de museus; exige internet e revisão humana."""
import argparse
import csv
import json
import sqlite3
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

TERMOS = {"Atena": ["Athena", "Minerva"], "Zeus": ["Zeus", "Jupiter"],
          "Afrodite": ["Aphrodite", "Venus"], "Apolo": ["Apollo"],
          "Héracles": ["Herakles", "Hercules"], "Medusa": ["Medusa", "Gorgon"]}
FIELDS_AIC = "id,title,artist_display,date_display,date_start,medium_display,artwork_type_title,image_id,is_public_domain"


def get_json(url):
    req = Request(url, headers={"User-Agent": "MythologyInArtPortfolio/0.1 (educational research)"})
    with urlopen(req, timeout=25) as resp:
        return json.load(resp)


def coletar_met(termo, limite):
    base = "https://collectionapi.metmuseum.org/public/collection"
    busca = get_json(base + "/v1.1/search?" + urlencode({"q": termo, "hasImages": "true", "limit": limite}))
    resultado = []
    for object_id in busca.get("objectIDs") or []:
        try:
            obj = get_json(base + "/v1/objects/" + str(object_id))
            if obj.get("isPublicDomain") and obj.get("primaryImageSmall"):
                resultado.append({"museu": "The Met", "obra_id": str(object_id),
                    "titulo": obj.get("title") or "", "artista": obj.get("artistDisplayName") or obj.get("culture") or "",
                    "data": obj.get("objectDate") or "", "ano_inicio": obj.get("objectBeginDate") or "",
                    "material": obj.get("medium") or "", "classificacao": obj.get("classification") or "",
                    "imagem": obj["primaryImageSmall"], "fonte": obj.get("objectURL") or "",
                    "dominio_publico": 1})
        except (OSError, ValueError) as exc:
            print(f"Falha em Met {object_id}: {exc}")
        time.sleep(0.12)
    return resultado


def coletar_aic(termo, limite):
    base = "https://api.artic.edu/api/v1/artworks/search?"
    payload = get_json(base + urlencode({"q": termo, "limit": limite, "fields": FIELDS_AIC,
                                          "query[term][is_public_domain]": "true"}))
    iiif = payload.get("config", {}).get("iiif_url", "https://www.artic.edu/iiif/2")
    resultado = []
    for obj in payload.get("data", []):
        if not obj.get("is_public_domain") or not obj.get("image_id"):
            continue
        resultado.append({"museu": "Art Institute of Chicago", "obra_id": str(obj["id"]),
            "titulo": obj.get("title") or "", "artista": obj.get("artist_display") or "",
            "data": obj.get("date_display") or "", "ano_inicio": obj.get("date_start") or "",
            "material": obj.get("medium_display") or "", "classificacao": obj.get("artwork_type_title") or "",
            "imagem": iiif + "/" + obj["image_id"] + "/full/843,/0/default.jpg",
            "fonte": "https://www.artic.edu/artworks/" + str(obj["id"]), "dominio_publico": 1})
    return resultado


def salvar(saida, obras, associacoes):
    saida.mkdir(parents=True, exist_ok=True)
    cols = ["museu", "obra_id", "titulo", "artista", "data", "ano_inicio", "material",
            "classificacao", "imagem", "fonte", "dominio_publico"]
    with (saida / "obras.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(obras.values())
    with (saida / "associacoes.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(["museu", "obra_id", "personagem", "termo_busca"])
        w.writerows(sorted(associacoes))
    with sqlite3.connect(saida / "mythology.sqlite") as db:
        db.execute("DROP TABLE IF EXISTS obras")
        db.execute("DROP TABLE IF EXISTS associacoes")
        db.execute("CREATE TABLE obras (museu TEXT, obra_id TEXT, titulo TEXT, artista TEXT, data TEXT, ano_inicio INTEGER, material TEXT, classificacao TEXT, imagem TEXT, fonte TEXT, dominio_publico INTEGER, PRIMARY KEY(museu,obra_id))")
        db.execute("CREATE TABLE associacoes (museu TEXT, obra_id TEXT, personagem TEXT, termo_busca TEXT, PRIMARY KEY(museu,obra_id,personagem,termo_busca))")
        db.executemany("INSERT INTO obras VALUES (?,?,?,?,?,?,?,?,?,?,?)", [tuple(o[c] for c in cols) for o in obras.values()])
        db.executemany("INSERT INTO associacoes VALUES (?,?,?,?)", sorted(associacoes))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-por-termo", type=int, default=20)
    parser.add_argument("--saida", type=Path, default=Path("dados"))
    args = parser.parse_args()
    if not 1 <= args.max_por_termo <= 500:
        parser.error("--max-por-termo deve estar entre 1 e 500")
    obras, associacoes = {}, set()
    for personagem, nomes in TERMOS.items():
        for termo in nomes:
            for fonte in (coletar_met, coletar_aic):
                try:
                    lote = fonte(termo, args.max_por_termo)
                    for obj in lote:
                        chave = (obj["museu"], obj["obra_id"])
                        obras[chave] = obj
                        associacoes.add((*chave, personagem, termo))
                    print(personagem, termo, fonte.__name__, len(lote))
                except (OSError, ValueError) as exc:
                    print(f"Falha em {fonte.__name__} para {termo}: {exc}")
                time.sleep(1)
    salvar(args.saida, obras, associacoes)
    print(f"{len(obras)} obras candidatas e {len(associacoes)} associações. Revise antes de inferir padrões.")


if __name__ == "__main__":
    main()
