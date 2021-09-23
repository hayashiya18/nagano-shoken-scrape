import os
import os.path as op
from datetime import datetime

import click
import pytz

from .scraper import Scraper


@click.group()
def main():
    pass


@main.command()
@click.argument("output_dir")
@click.argument("shiten_num")
@click.argument("koza_num")
@click.argument("password")
def make_csv(output_dir: str, shiten_num: str, koza_num: str, password: str):
    os.makedirs(output_dir, exist_ok=True)
    scraper = Scraper(shiten_num, koza_num, password)
    df = scraper.run()
    now = datetime.now(pytz.timezone("Asia/Tokyo"))
    savepath = op.join(output_dir, f"{now.isoformat()}.csv")
    df.to_csv(savepath, index=None)


if __name__ == "__main__":
    main()
