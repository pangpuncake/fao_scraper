import pandas as pd
import logging
from datetime import datetime
from typing import List, Tuple
from models import (
    CommoditySubCategory,
    CommodityType,
    Commodity,
    CommodityDetail,
    CommodityMRL,
    PesticideDetail,
    PesticideMRL,
)
from api import get_commodity_category, get_commodity_detail, get_pesticide_detail

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    commodity_category_ls = get_commodity_category()

    commodity_sub_category_ls: List[CommoditySubCategory] = []
    for commodity_category in commodity_category_ls:
        commodity_sub_category_ls.extend(list(commodity_category.get_children()))

    commodity_type_ls: List[CommodityType] = []
    for commodity_sub_category in commodity_sub_category_ls:
        commodity_type_ls.extend(list(commodity_sub_category.get_children()))

    commodity_ls: List[Commodity] = []
    for commodity_type in commodity_type_ls:
        commodity_ls.extend(list(commodity_type.get_children()))

    commodity_error_ids: List[str] = []
    commodity_detail_ls: List[CommodityDetail] = []
    for commodity in commodity_ls:
        commodity_id = commodity.get_id()
        try:
            commodity_detail = get_commodity_detail(commodity_id)
        except:
            logger.error(f"Failed to get commodity with id={commodity_id}", exc_info=1)
            commodity_error_ids.append(commodity_id)
            continue
        commodity_detail_ls.append(commodity_detail)

    commodity_mrl_ls: List[Tuple[str, List[CommodityMRL]]] = []
    for commodity_detail in commodity_detail_ls:
        commodity_mrls = commodity_detail.get_commodity_mrls()
        if commodity_mrls is None:
            continue
        commodity_mrl_ls.append(commodity_mrls)

    commodity_mrl_series_ls: List[pd.Series] = []
    pesticide_detail_ls: List[PesticideDetail] = []
    pesticide_id_set = set()
    pesticide_error_ids: List[str] = []
    for commodity, mrl_ls in commodity_mrl_ls:
        for mrl in mrl_ls:
            commodity_mrl_series_ls.append(mrl.get_mrl_series(commodity))
            pesticide_id = mrl.pesticide.id
            if pesticide_id in pesticide_id_set:
                continue
            pesticide_id_set.add(pesticide_id)
            try:
                pesticide_detail = get_pesticide_detail(pesticide_id)
            except:
                logger.error(
                    f"Failed to get pesticide with id={pesticide_id}", exc_info=1
                )
                pesticide_error_ids.append(pesticide_id)
                continue
            pesticide_detail_ls.append(pesticide_detail)

    pesticide_mrl_ls: List[Tuple[str, List[PesticideMRL]]] = []
    for pesticide_detail in pesticide_detail_ls:
        pesticide_mrls = pesticide_detail.get_pesticide_mrls()
        if pesticide_mrls is None:
            continue
        pesticide_mrl_ls.append(pesticide_mrls)

    pesticide_mrl_series_ls: List[pd.Series] = []
    for pesticide, mrl_ls in pesticide_mrl_ls:
        for mrl in mrl_ls:
            pesticide_mrl_series_ls.append(mrl.get_mrl_series(pesticide))

    commodity_mrl_df = pd.DataFrame(commodity_mrl_series_ls)
    pesticide_mrl_df = pd.DataFrame(pesticide_mrl_series_ls)
    pesticide_df = pd.DataFrame(
        [
            pesticide_detail.get_pesticide_detail_series()
            for pesticide_detail in pesticide_detail_ls
        ]
    )

    logger.info(commodity_mrl_df.head())
    logger.info(pesticide_mrl_df.head())
    logger.info(pesticide_df.head())

    commodity_mrl_path = f"./output/commodity_mrl_codex_alimentarius_{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}.csv"
    pesticide_mrl_path = f"./output/pesticide_mrl_codex_alimentarius_{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}.csv"
    pesticide_path = f"./output/pesticide_codex_alimentarius_{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}.csv"

    commodity_mrl_df.to_csv(commodity_mrl_path, index=False)
    pesticide_mrl_df.to_csv(pesticide_mrl_path, index=False)
    pesticide_df.to_csv(pesticide_path, index=False)
    logger.info(f"Saved Commodity MRL Info to {commodity_mrl_path}")
    logger.info(f"Saved Pesticide MRL Info to {pesticide_mrl_path}")
    logger.info(f"Saved Pesticide Info to {pesticide_path}")
    logger.info(f"Failed commodity ids: {commodity_error_ids}")
    logger.info(f"Failed pesticide ids: {pesticide_error_ids}")
    logger.info("Done!")


if __name__ == "__main__":
    import time

    start_time = time.perf_counter()
    main()
    end_time = time.perf_counter()
    logger.info(f"Time taken: {end_time - start_time}")
