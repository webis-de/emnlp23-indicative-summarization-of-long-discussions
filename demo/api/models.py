from typing import Any, Dict, List, Optional

from bson.objectid import ObjectId
from humps import camelize
from pydantic import AnyUrl, BaseModel, ConfigDict, Field
from pydantic_core import core_schema


class ObjectIdField(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        object_id_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(cls.validate),
            ]
        )
        return core_schema.json_or_python_schema(
            json_schema=object_id_schema,
            python_schema=core_schema.union_schema(
                [core_schema.is_instance_schema(ObjectId), object_id_schema]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def validate(cls, value):
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid id")

        return ObjectId(value)


class CommentModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=camelize)

    id: str
    name: str
    parent: Optional[str] = None
    author: Optional[str] = None
    text: List[str] = []
    comments: Optional[List["CommentModel"]]
    is_submitter: bool


class PostModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=camelize)

    title: str
    url: AnyUrl
    root: CommentModel
    num_comments: int
    labels: Dict[str, Dict[str, str]] = {}
    cluster_model: str
    result: Dict[str, List]
    meta: Dict[str, Any] = {}
    frames: Optional[Dict] = None


class StoredOverviewModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: ObjectIdField
    title: str
    url: AnyUrl
    num_comments: int = Field(alias="numComments")
    labels: List[str]


class LabelsModel(BaseModel):
    labels: Dict[str, Dict[str, str]]
    frames: Optional[Dict]
    result: Dict[str, List]
    root: CommentModel
    meta: Optional[Dict]


class PrecomputedOverviewModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=camelize)

    id: str
    title: str
    url: AnyUrl
    num_comments: int
    labels: List[str]
