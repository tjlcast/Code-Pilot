#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time 2023/11/3 S{TIME} 
# @Name Response. Py
# @Author：jialtang
import json
from typing import *

import pydantic
from pydantic import BaseModel


class BaseResponse(BaseModel):
    code: int = pydantic.Field(200, description="API status code")
    msg: str = pydantic.Field("success", description="API status message")
    data: Any = pydantic.Field(None, description="API data")

    class Config:
        schema_extra = {
            "example": {
                "code": 200,
                "msg": "success",
            }
        }

    @classmethod
    def from_msg(cls, msg: str):
        return cls(code=200, msg=msg)

    @classmethod
    def from_dict(cls, response: dict):
        return cls(code=response["code"], msg=response["msg"], data=response["data"])

    @classmethod
    def from_json_str(cls, text: str):
        resp_dict = json.loads(text)
        from_dict = BaseResponse.from_dict(resp_dict)
        return from_dict


if __name__ == "__main__":
    print("hello")
