#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time 2023/11/2 S{TIME} 
# @Name api. Py
# @Author：jialtang

import contextlib
import json
import os
from contextlib import asynccontextmanager, contextmanager
from pprint import pprint
from typing import *

import httpx

# 此处导入的配置为发起请求（如WEBUI）机器上的配置，主要用于为前端设置默认值。分布式部署时可以与服务器上的不同
from configs.log_config import (
    logger, log_verbose,
)


class OpenAiApiRequest:
    '''
    api.py调用的封装（同步模式）,简化api调用方式
    '''

    def __init__(
            self,
            base_url: str,
            # httpx 请求默认超时时间（秒）。如果加载模型或对话较慢，出现超时错误，可以适当加大该值。
            timeout: float = 300.0,
    ):
        self.base_url = base_url
        self.timeout = timeout
        self._use_async = False
        self._client = None
        self.auth = ("Authorization", os.environ.get("OPENAI_API_KEY", ""))

    @property
    def client(self):
        if self._client is None or self._client.is_closed:
            self._client = get_httpx_client(base_url=self.base_url,
                                            use_async=self._use_async,
                                            timeout=self.timeout)
        return self._client

    def delete(self,
               url: str,
               retry: int = 3,
               **kwargs: Any
               ) -> Union[httpx.Response, None]:
        while retry > 0:
            try:
                return self.client.delete(url, params=None, **kwargs)
            except Exception as e:
                msg = f"error when post {url}: {e}"
                logger.error(f'{e.__class__.__name__}: {msg}',
                             exc_info=e if log_verbose else None)
                retry -= 1

    def get(self,
            url: str,
            data: Dict = None,
            json: Dict = None,
            retry: int = 3,
            **kwargs: Any
            ) -> Union[httpx.Response, None]:
        while retry > 0:
            try:
                return self.client.get(url, params=data, **kwargs)
            except Exception as e:
                msg = f"error when post {url}: {e}"
                logger.error(f'{e.__class__.__name__}: {msg}',
                             exc_info=e if log_verbose else None)
                retry -= 1

    def get_as_json(self,
                    url: str,
                    data: Dict = None,
                    retry: int = 3,
                    **kwargs: Any
                    ) -> Union[dict, list, None]:
        try:
            response = self.get(url=url, data=data, retry=retry, **kwargs)
            return json.loads(response.text)
        except httpx.ConnectError as e:
            msg = f"无法连接API服务器，请确认 ‘api.py’ 已正常启动。({e})"
            logger.error(msg)
            print({"code": 500, "msg": msg})
        except httpx.ReadTimeout as e:
            msg = f"API通信超时，请确认已启动FastChat与API服务（详见Wiki '5. 启动 API 服务或 Web UI'）。（{e}）"
            logger.error(msg)
            print({"code": 500, "msg": msg})
        except Exception as e:
            msg = f"API通信遇到错误：{e}"
            logger.error(f'{e.__class__.__name__}: {msg}',
                         exc_info=e if log_verbose else None)
            print({"code": 500, "msg": msg})

    @contextmanager
    def _post(self,
              url: str,
              data: Dict = None,
              json: Dict = None,
              **kwargs: Any
              ) -> Iterator[httpx.Response]:

        resposne = self.client.post(url, data=data, json=json, **kwargs)
        try:
            yield resposne
        finally:
            resposne.close()

    @asynccontextmanager
    async def _asyncpost(self,
                         url: str,
                         data: Dict = None,
                         json: Dict = None,
                         **kwargs: Any
                         ) -> Iterator[httpx.Response]:

        resposne = await self.client.post(url, data=data, json=json, **kwargs)
        try:
            yield resposne
        finally:
            await resposne.aclose()

    def post(
            self,
            url: str,
            data: Dict = None,
            json: Dict = None,
            retry: int = 3,
            stream: bool = False,
            **kwargs: Any
    ) -> Union[httpx.Response, Iterator[httpx.Response], None]:
        while retry > 0:
            try:
                if stream:
                    return self.client.stream("POST", url, data=data, json=json, **kwargs)
                else:
                    # 不是异步情况
                    if not self._use_async:
                        return self._post(url, data=data, json=json, **kwargs)
                    # 使用异步
                    else:
                        return self._asyncpost(url, data=data, json=json, **kwargs)
            except Exception as e:
                msg = f"error when post {url}: {e}"
                logger.error(f'{e.__class__.__name__}: {msg}',
                             exc_info=e if log_verbose else None)
                retry -= 1

    def _httpx_stream2generator(
            self,
            response: contextlib._GeneratorContextManager,
            stream: bool = True,
            as_json: bool = False,
    ):
        '''
        将httpx.stream返回的GeneratorContextManager转化为普通生成器
        '''

        async def ret_async(response, as_json):
            try:
                async with response as r:
                    # 返回是非流式的情况
                    if not stream:
                        # 是否返回json格式
                        if as_json:
                            try:
                                yield r.json()
                            except Exception as e:
                                msg = f"接口返回json错误： ‘{r.content}’。错误信息是：{e}。"
                                logger.error(f'{e.__class__.__name__}: {msg}',
                                             exc_info=e if log_verbose else None)
                        # 直接返回string
                        else:
                            yield r.content
                    # 返回是流式的情况
                    else:
                        # async for chunk in r.aiter_text(None):
                        async for chunk in r.aiter_lines():
                            if not chunk or chunk.startswith("data: [DONE]"):  # fastchat api yield empty bytes on start and end
                                continue
                            # 是否返回json格式
                            if as_json:
                                try:
                                    if chunk.startswith("data: "):
                                        chunk = chunk[len("data: "):]
                                    data = json.loads(chunk)
                                    # pprint(data, depth=1)
                                    yield data
                                except Exception as e:
                                    msg = f"接口返回json错误： ‘{chunk}’。错误信息是：{e}。"
                                    logger.error(f'{e.__class__.__name__}: {msg}',
                                                 exc_info=e if log_verbose else None)
                            # 直接返回string
                            else:
                                # print(chunk, end="", flush=True)
                                yield chunk
            except httpx.ConnectError as e:
                msg = f"无法连接API服务器，请确认 ‘api.py’ 已正常启动。({e})"
                logger.error(msg)
                yield {"code": 500, "msg": msg}
            except httpx.ReadTimeout as e:
                msg = f"API通信超时，请确认已启动FastChat与API服务（详见Wiki '5. 启动 API 服务或 Web UI'）。（{e}）"
                logger.error(msg)
                yield {"code": 500, "msg": msg}
            except Exception as e:
                msg = f"API通信遇到错误：{e}"
                logger.error(f'{e.__class__.__name__}: {msg}',
                             exc_info=e if log_verbose else None)
                yield {"code": 500, "msg": msg}

        def ret_sync(response, as_json):
            try:
                with response as r:
                    # 返回是非流式的情况
                    if not stream:
                        # 是否返回json格式
                        if as_json:
                            try:
                                yield r.json()
                            except Exception as e:
                                msg = f"接口返回json错误： ‘{r.content}’。错误信息是：{e}。"
                                logger.error(f'{e.__class__.__name__}: {msg}',
                                             exc_info=e if log_verbose else None)
                        # 直接返回string
                        else:
                            yield r.content
                    # 返回是流式的情况
                    else:
                        # for chunk in r.iter_text(None):
                        for chunk in r.iter_lines():
                            if (not chunk) or chunk.startswith("data: [DONE]"):  # fastchat api yield empty bytes on start and end
                                continue
                            # 是否返回json格式
                            if as_json:
                                try:
                                    if chunk.startswith("data: "):
                                        chunk = chunk[len("data: "):]
                                    data = json.loads(chunk)
                                    # pprint(data, depth=1)
                                    yield data
                                except Exception as e:
                                    msg = f"接口返回json错误： ‘{chunk}’。错误信息是：{e}。"
                                    logger.error(f'{e.__class__.__name__}: {msg}',
                                                 exc_info=e if log_verbose else None)
                            # 直接返回string
                            else:
                                # print(chunk, end="", flush=True)
                                yield chunk
            except httpx.ConnectError as e:
                msg = f"无法连接API服务器，请确认 ‘api.py’ 已正常启动。({e})"
                logger.error(msg)
                yield {"code": 500, "msg": msg}
            except httpx.ReadTimeout as e:
                msg = f"API通信超时，请确认已启动FastChat与API服务（详见Wiki '5. 启动 API 服务或 Web UI'）。（{e}）"
                logger.error(msg)
                yield {"code": 500, "msg": msg}
            except Exception as e:
                msg = f"API通信遇到错误：{e}"
                logger.error(f'{e.__class__.__name__}: {msg}',
                             exc_info=e if log_verbose else None)
                yield {"code": 500, "msg": msg}

        if self._use_async:
            return ret_async(response, as_json)
        else:
            return ret_sync(response, as_json)

    def chat_completion(self,
                        data_str: str,
                        as_json: bool = False,
                        **kwargs):
        """
        根据async、stream、json请求接口并处理返回结果
        """
        data = json.loads(data_str)
        stream = data.get("stream", True)
        url = os.environ.get("OPENAI_API_URL", "/v1/chat/completions")
        response = self.post(url, json=data, stream=stream, auth=self.auth, **kwargs)
        return self._httpx_stream2generator(response, stream, as_json)

    def chat_completion_v1(self,
                           query: str,
                           history: List,
                           model: str,
                           temperature: float = 0.7,
                           stream: bool = True,
                           as_json: bool = False,
                           **kwargs):
        """
        根据async、stream、json请求接口并处理返回结果
        """
        messages = []
        messages.extend(history)
        messages.append({"role": "user", "content": query})
        data = {
            "temperature": temperature,
            "model": model,
            "stream": stream,
            "messages": messages,
        }
        url = os.environ.get("OPENAI_API_URL", "/v1/chat/completions")
        response = self.post(url, json=data, stream=stream, auth=self.auth, **kwargs)
        return self._httpx_stream2generator(response, stream, as_json)

    def chat_chat(
            self,
            query: str,
            history: List[Dict] = [],
            stream: bool = True,
            # model: str = "gpt-3.5-turbo",
            model: str = "OpenAI",
            temperature: float = 0.7,
            max_tokens: int = None,
            prompt_name: str = "default",
            **kwargs,
    ):
        '''
        对应api.py/chat/chat接口 #TODO: 考虑是否返回json
        '''
        data = {
            "query": query,
            "history": history,
            "stream": stream,
            "model_name": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "prompt_name": prompt_name,
        }

        print(f"received input message:")
        pprint(data)
        response = self.post("/chat/chat", json=data, stream=True, **kwargs)
        return self._httpx_stream2generator(response)


def get_httpx_client(
        use_async: bool = False,
        proxies: Union[str, Dict] = None,
        timeout: float = 300.0,
        **kwargs,
) -> Union[httpx.Client, httpx.AsyncClient]:
    '''
    helper to get httpx client with default proxies that bypass local addesses.
    '''
    default_proxies = {
        # do not use proxy for locahost
        "all://127.0.0.1": None,
        "all://localhost": None,
    }
    # do not use proxy for user deployed fastchat servers
    # for x in [
    #     fschat_controller_address(),
    #     fschat_model_worker_address(),
    #     fschat_openai_api_address(),
    # ]:
    #     host = ":".join(x.split(":")[:2])
    #     default_proxies.update({host: None})

    # get proxies from system envionrent
    # proxy not str empty string, None, False, 0, [] or {}
    default_proxies.update({
        "http://": (os.environ.get("http_proxy")
                    if os.environ.get("http_proxy") and len(os.environ.get("http_proxy").strip())
                    else None),
        "https://": (os.environ.get("https_proxy")
                     if os.environ.get("https_proxy") and len(os.environ.get("https_proxy").strip())
                     else None),
        "all://": (os.environ.get("all_proxy")
                   if os.environ.get("all_proxy") and len(os.environ.get("all_proxy").strip())
                   else None),
    })
    for host in os.environ.get("no_proxy", "").split(","):
        if host := host.strip():
            default_proxies.update({host: None})

    # merge default proxies with user provided proxies
    if isinstance(proxies, str):
        proxies = {"all://": proxies}

    if isinstance(proxies, dict):
        default_proxies.update(proxies)

    # construct Client
    kwargs.update(timeout=timeout, proxies=default_proxies)
    print(kwargs)
    if use_async:
        return httpx.AsyncClient(**kwargs)
    else:
        return httpx.Client(**kwargs)


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8080
    url = f"http://{host}:{port}"
    url = "https://api.openai.com"

    api = OpenAiApiRequest(base_url=url)
    # response = api.get("/genspace/")
    # response_json = api.get_as_json("/genspace/")
    # auth = ("Authorization", os.environ["OPENAI_API_KEY"])
    data_str = """
                {
                  "model": "gpt-3.5-turbo",
                  "stream": true,
                  "messages": [
                    {
                      "role": "system",
                      "content": "You are a helpful assistant."
                    },
                    {
                      "role": "user",
                      "content": "Hello!"
                    }
                  ]
                }"""
    completionGens = api.chat_completion(data_str, as_json=True)
    for t in completionGens:
        print(f"say: {t}")
    # print(f'{response} - {response_json}')
