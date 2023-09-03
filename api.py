import logging
import requests
import backoff
import json

from datetime import datetime
from typing import List
from models import CommodityCategory, CommodityDetail, PesticideDetail

COMMODITY_CATEGORY_URL = "https://www.fao.org/fileadmin/templates/codexalimentarius/pestres/codex-commodities-en.json"
COMMODITY_DETAIL_URL = (
    "https://www.fao.org/jsoncodexpest/jsonrequest/commodities/details.html"
)
PESTICIDE_DETAIL_URL = (
    "https://www.fao.org/jsoncodexpest/jsonrequest/pesticides/details.html"
)


logger = logging.getLogger(__name__)


def get_commodity_category(d: datetime = datetime.now()) -> List[CommodityCategory]:
    logger.info("Getting commodity categories")
    ms_since_epoch = int(d.timestamp() * 1000)
    url = COMMODITY_CATEGORY_URL + f"?{ms_since_epoch}"
    response = requests.get(url)
    response_json = response.json()

    res = []
    for comm_cat_json in response_json:
        res.append(CommodityCategory.model_validate(comm_cat_json))
    return res


@backoff.on_exception(
    backoff.expo,
    [requests.exceptions.JSONDecodeError],
    max_tries=5,
    logger=logger,
)
def get_commodity_detail(id: str) -> CommodityDetail:
    logger.info(f"Getting commodity detail with id={id}")
    url = COMMODITY_DETAIL_URL + f"?id={id}&lang=en"
    response = requests.get(url)
    # Replace erroneous characters
    response_text = (
        response.text.replace("\t", "").replace("\u2013", "-").replace("\x03", " ")
    )
    response_json = json.loads(response_text)
    return CommodityDetail.model_validate(response_json)


@backoff.on_exception(
    backoff.expo,
    [requests.exceptions.JSONDecodeError],
    max_tries=5,
    logger=logger,
)
def get_pesticide_detail(id: str) -> PesticideDetail:
    logger.info(f"Getting pesticide detail with id={id}")
    url = PESTICIDE_DETAIL_URL + f"?id={id}&lang=en"
    response = requests.get(url)
    # Replace erroneous characters
    response_text = (
        response.text.replace("\t", "").replace("\u2013", "-").replace("\x03", " ")
    )
    response_json = json.loads(response_text)
    return PesticideDetail.model_validate(response_json)


if __name__ == "__main__":
    # For testing purposes, when required
    get_pesticide_detail("269")
