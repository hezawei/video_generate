import time
import requests

# 悟隐科技 Sora2 接口配置
API_KEY = "Kp2Awh23NjJeIrLTkZANHhFDWw"
SUBMIT_URL = "https://api.wuyinkeji.com/api/sora2/submit"
DETAIL_URL = "https://api.wuyinkeji.com/api/sora2/detail"


def submit_video() -> str | None:
    """提交生成任务，返回任务 ID（data.id）。"""
    headers = {
        "Authorization": API_KEY,
        # 按文档要求的 Content-Type
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
    }
    # 文档示例里也带了 ?key=你的密钥，这里同时带上
    params = {
        "key": API_KEY,
    }
    data = {
        "prompt": "小猫钓鱼",  # 最简单的测试文案
        "aspectRatio": "9:16",
        "duration": "10",      # 10 秒
        "size": "small",       # 文档推荐 small
    }

    print("1. 提交生成任务...")
    resp = requests.post(SUBMIT_URL, headers=headers, params=params, data=data, timeout=30)
    print("提交返回:", resp.status_code, resp.text)

    try:
        resp.raise_for_status()
        js = resp.json()
    except Exception as e:
        print("解析提交结果出错:", e)
        return None

    if js.get("code") != 200:
        print("提交失败:", js)
        return None

    data_obj = js.get("data") or {}
    task_id = data_obj.get("id")
    print("任务 ID:", task_id)
    return task_id


def poll_video(task_id: str, max_attempts: int = 60, interval: int = 5) -> str | None:
    """轮询查询任务状态，成功时返回 remote_url。"""
    headers = {
        "Authorization": API_KEY,
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
    }

    for i in range(1, max_attempts + 1):
        params = {
            "key": API_KEY,
            "id": task_id,
        }
        print(f"\n2. 第 {i} 次查询任务状态...")
        resp = requests.get(DETAIL_URL, headers=headers, params=params, timeout=30)
        print("查询返回:", resp.status_code, resp.text)

        try:
            resp.raise_for_status()
            js = resp.json()
        except Exception as e:
            print("解析查询结果出错:", e)
            time.sleep(interval)
            continue

        if js.get("code") != 200:
            print("查询接口返回异常:", js)
            time.sleep(interval)
            continue

        data_obj = js.get("data") or {}
        status = data_obj.get("status")  # 0 排队中，1 成功，2 失败, 3 生成中
        print("当前状态:", status)

        if status == 1:
            remote_url = data_obj.get("remote_url")
            print("\n生成成功，视频地址 remote_url:", remote_url)
            return remote_url
        elif status == 2:
            print("\n生成失败，原因:", data_obj.get("fail_reason"))
            return None

        time.sleep(interval)

    print("\n轮询超时，可能还在排队或生成中，请稍后再查 detail 接口。")
    return None


if __name__ == "__main__":
    tid = submit_video()
    if tid:
        poll_video(tid)
