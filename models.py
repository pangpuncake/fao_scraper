import pydantic
import pandas as pd
from typing import Dict, List, Optional, Generator, Tuple


"""
Skeleton of website directory structure

CommodityCategory
    - CommoditySubCategory
        - CommodityType
            - Commodity
"""


class CommodityBaseJsonObject(pydantic.BaseModel):
    id: str = pydantic.Field(...)
    metadata: Dict[str, str] = pydantic.Field(...)
    data: str = pydantic.Field(...)


class ParentDirectory:
    def get_children(self) -> Generator[CommodityBaseJsonObject, None, None]:
        raise NotImplementedError("All parent directories must implement this method.")


class Commodity(CommodityBaseJsonObject):
    def get_id(self) -> str:
        return self.metadata["id"]


class CommodityType(CommodityBaseJsonObject, ParentDirectory):
    children: Optional[List[Commodity]] = None

    def get_children(self) -> Generator[Commodity, None, None]:
        if self.children is None:
            return None
        for child in self.children:
            yield child


class CommoditySubCategory(CommodityBaseJsonObject, ParentDirectory):
    children: List[CommodityType]

    def get_children(self) -> Generator[CommodityType, None, None]:
        for child in self.children:
            yield child


class CommodityCategory(CommodityBaseJsonObject, ParentDirectory):
    children: List[CommoditySubCategory]

    def get_children(self) -> Generator[CommoditySubCategory, None, None]:
        for child in self.children:
            yield child


class Pesticide(pydantic.BaseModel):
    name: str
    id: str


class BaseMRL(pydantic.BaseModel):
    mrl: Optional[float]
    mrl_formatted: str = pydantic.Field(alias="mrlFormatted", default="")
    jmpr: str
    ccpr: str
    prior_ccpr: str = pydantic.Field(..., alias="priorCcpr")
    cac_year: str = pydantic.Field(..., alias="cacYear")
    lod: str
    source_of_res: str = pydantic.Field(..., alias="sourceOfRes")
    fat_ph: str = pydantic.Field(..., alias="fatPh")
    tev: str
    footnote: str
    footnote_ccpr: str = pydantic.Field(..., alias="footnoteCcpr")
    commodity: Dict[str, str]

    @pydantic.field_validator("mrl", mode="before")
    @classmethod
    def empty_str_to_none(cls, v: str) -> Optional[str]:
        if v == "":
            return None
        return v


class PesticideMRL(BaseMRL):
    step: Dict[str, str]

    def get_mrl_series(self, pesticide: str) -> pd.Series:
        mrl_dict = self.model_dump()
        mrl_dict["pesticide"] = pesticide
        mrl_dict["commodity_code"] = mrl_dict["commodity"]["commCode"]
        mrl_dict["commodity_name"] = mrl_dict["commodity"]["name"]
        # Delete commodity key
        mrl_dict["step"] = mrl_dict["step"]["stepCode"]
        mrl_dict.pop("commodity", None)
        return pd.Series(mrl_dict)


class CommodityMRL(BaseMRL):
    pesticide: Pesticide

    def get_mrl_series(self, commodity: str) -> pd.Series:
        mrl_dict = self.model_dump()
        mrl_dict["pesticide"] = mrl_dict["pesticide"]["name"]
        mrl_dict["commodity_code"] = mrl_dict["commodity"]["commCode"]
        mrl_dict["commodity_name"] = commodity
        # Delete commodity key
        mrl_dict.pop("commodity", None)
        return pd.Series(mrl_dict)


class CommodityDetail(pydantic.BaseModel):
    commodity: str
    comm_code: str = pydantic.Field(..., alias="commCode")
    mrls: Optional[Dict[str, List[CommodityMRL]]] = None
    symbols: Optional[Dict[str, List[Dict[str, str]]]] = None

    def get_commodity_mrls(self) -> Optional[Tuple[str, List[CommodityMRL]]]:
        if self.mrls is None:
            return None
        return (self.commodity, self.mrls["mrl"])


class PesticideDetail(pydantic.BaseModel):
    name: str
    pest_id_codex: str = pydantic.Field(alias="pestIdCodex")
    pesticide: str
    adi: str
    adi_unit: str = pydantic.Field(alias="adiUnit")
    adi_note: str = pydantic.Field(alias="adiNote")
    vetd_flag: str = pydantic.Field(alias="vetdFlag")
    residue: str
    note: Dict[str, str]
    mrls: Optional[Dict[str, List[PesticideMRL]]] = None

    def get_pesticide_mrls(self) -> Optional[Tuple[str, List[CommodityMRL]]]:
        if self.mrls is None:
            return None
        return (self.pesticide, self.mrls["mrl"])

    def get_pesticide_detail_series(self) -> pd.Series:
        pesticide_detail_dict = self.model_dump()
        pesticide_detail_dict["note"] = pesticide_detail_dict["note"].get("en", "")
        # Drop the mrls key
        pesticide_detail_dict.pop("mrls", None)
        return pd.Series(pesticide_detail_dict)
