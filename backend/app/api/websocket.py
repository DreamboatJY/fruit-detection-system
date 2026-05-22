from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.camera_detection_service import camera_detection_service

router = APIRouter(prefix="/api", tags=["websocket"])


@router.websocket("/camera/detect")
async def camera_detect(websocket: WebSocket):
    """
    摄像头实时检测WebSocket端点
    前端发送base64编码的图像帧，后端返回检测结果和标注图像
    """
    await websocket.accept()
    print("摄像头检测连接已建立")

    try:
        while True:
            # 接收前端发送的图像帧数据
            data = await websocket.receive_text()

            # 解析JSON数据
            import json
            payload = json.loads(data)
            frame_data = payload.get("frame", "")
            model_name = payload.get("model_name", "pest-v1")

            if not frame_data:
                await websocket.send_json({
                    "success": False,
                    "error": "未接收到图像数据"
                })
                continue

            # 执行检测
            result = camera_detection_service.detect_frame(frame_data)

            # 发送检测结果
            await websocket.send_json(result)

    except WebSocketDisconnect:
        print("摄像头检测连接已断开")
    except Exception as e:
        print(f"摄像头检测错误: {e}")
        try:
            await websocket.send_json({
                "success": False,
                "error": str(e)
            })
        except:
            pass
