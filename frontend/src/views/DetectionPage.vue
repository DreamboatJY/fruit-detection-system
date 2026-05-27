<template>
  <div class="detection-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="breadcrumb">
        <span>工作台</span>
        <span class="separator">›</span>
        <span class="active">智能检测</span>
      </div>
      <h1 class="page-title">上传钢材表面图像，立即识别六类缺陷</h1>
      <p class="page-subtitle">
        支持裂纹 / 夹杂物 / 斑块 / 麻面 / 轧制氧化皮 / 划痕等多缺陷检测
      </p>
    </div>

    <!-- 模型选择器 -->
    <div class="model-selector">
      <el-select v-model="selectedModel" style="width: 180px">
        <el-option label="neu-det-yolo11n" value="neu-det-yolo11n" />
      </el-select>
    </div>

    <!-- 功能选项卡 -->
    <div class="function-tabs">
      <div
        v-for="tab in functionTabs"
        :key="tab.key"
        class="function-tab"
        :class="{ active: activeTab === tab.key }"
        :data-key="tab.key"
        @click="handleTabClick(tab.key)"
      >
        <el-icon :size="18" class="tab-icon"
          ><component :is="tab.icon"
        /></el-icon>
        <div class="tab-content">
          <span class="tab-text">{{ tab.name }}</span>
          <span class="tab-desc">{{ tab.desc }}</span>
        </div>
      </div>
    </div>

    <!-- 批量检测上传区域 -->
    <div v-if="activeTab === 'batch'" class="batch-upload-area">
      <!-- 无待上传文件时，显示上传引导 -->
      <div v-if="!pendingBatchFiles.length && !batchResult" class="batch-upload-placeholder" @click="triggerBatchFileInput">
        <input
          type="file"
          accept="image/*"
          multiple
          class="batch-file-input"
          @change="handleFileChange($event, 'batch')"
          @click.stop
          ref="batchFileInputRef"
        />
        <el-icon class="batch-upload-icon"><Upload /></el-icon>
        <p class="batch-upload-text">点击此处选择图片或拖拽图片到此处</p>
        <p class="batch-upload-desc">支持 jpg、png 格式，单次最多 20 张图片</p>
        <el-button type="primary" size="small" class="batch-upload-btn">
          <el-icon><Plus /></el-icon>
          选择图片
        </el-button>
      </div>
      <!-- 有待上传文件时，显示待上传清单 -->
      <div v-if="pendingBatchFiles.length" class="upload-panel">
        <div class="upload-panel-header">
          <div>
            <span class="panel-title">待上传清单</span>
            <span class="upload-count">{{ pendingBatchFiles.length }} 张图片</span>
          </div>
          <div class="upload-actions">
            <el-button size="small" @click="pendingBatchFiles = []">清空</el-button>
            <el-button type="primary" size="small" @click="startPendingBatch">
              <el-icon><Upload /></el-icon>
              开始批量检测
            </el-button>
          </div>
        </div>
        <div class="upload-file-list">
          <div v-for="(file, index) in pendingBatchFiles" :key="`${file.name}-${index}`" class="upload-file">
            <span class="upload-file-name">{{ file.name }}</span>
            <span class="upload-file-size">{{ formatFileSize(file.size) }}</span>
            <el-button text size="small" @click="removePendingFile(index)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 左侧检测结果区域 -->
      <div class="left-panel">
        <div class="panel-header">
          <span class="panel-title">检测预览</span>
          <el-tag
            :type="hasDetectionContext && activeDetectionResult ? 'success' : 'info'"
            effect="light"
            class="result-tag"
          >
            <el-icon class="el-icon--left" v-if="hasDetectionContext && activeDetectionResult"
              ><Check
            /></el-icon>
            <el-icon class="el-icon--left" v-else><Upload /></el-icon>
            {{ resultStatusText }}
          </el-tag>
        </div>

        <CameraDetection
          v-if="activeTab === 'camera'"
          ref="cameraDetectionRef"
          @result-change="handleCameraResult"
          @running-change="handleCameraRunningChange"
        />

        <VideoDetection
          v-else-if="activeTab === 'video'"
          ref="videoDetectionRef"
          :model-name="selectedModel"
          @result-change="handleVideoResult"
          @running-change="handleVideoRunningChange"
          @context-change="handleVideoContextChange"
        />

        <!-- 图片对比区域 -->
        <div v-else class="image-compare">
          <div class="image-card">
            <input
              v-if="activeTab === 'single'"
              type="file"
              accept="image/*"
              class="single-file-input"
              @change="handleFileChange($event, 'single')"
              ref="singleFileInputRef"
            />
            <template v-if="hasImage && originalImage">
              <img :src="originalImage" alt="原始图片" class="compare-image" />
            </template>
            <template v-else>
              <div class="image-placeholder">
                <el-icon class="placeholder-icon"><Upload /></el-icon>
                <p class="placeholder-text">请上传图片</p>
                <p class="placeholder-desc">支持 jpg、png 格式</p>
              </div>
            </template>
            <div class="image-label">原始图片</div>
          </div>
          <div class="image-card">
            <template v-if="hasImage && resultImage">
              <img :src="resultImage" alt="检测结果" class="compare-image" />
              <div class="detection-mark" v-if="detectionResult"></div>
            </template>
            <template v-else>
              <div class="image-placeholder">
                <el-icon class="placeholder-icon"><View /></el-icon>
                <p class="placeholder-text">检测结果将在此展示</p>
                <p class="placeholder-desc">上传图片后开始检测</p>
              </div>
            </template>
            <div class="image-label">检测结果</div>
          </div>
        </div>
      </div>

      <!-- 右侧信息面板 -->
      <div class="right-panel">
        <!-- 模型信息 -->
        <div class="info-card">
          <div class="info-item">
            <span class="info-label">检测模型</span>
            <span class="info-value">{{ selectedModel }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">检测模式</span>
            <span class="info-value">{{ detectionModeText }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">模型版本</span>
            <span class="info-value">v1.0.0</span>
          </div>
        </div>

        <!-- 识别清单 -->
        <div class="result-card">
          <div class="card-header">
            <el-icon><List /></el-icon>
            <span class="card-title">识别清单</span>
          </div>
          <div v-if="!hasDetectionContext" class="empty-state">
            <el-icon class="empty-icon"><Upload /></el-icon>
            <p class="empty-text">{{ emptyStateText }}</p>
            <p class="empty-desc">{{ emptyStateDesc }}</p>
          </div>
          <div
            v-else-if="!activeDetectionResult || activeDetectionResult.total_objects === 0"
            class="empty-state"
          >
            <el-icon class="empty-icon"><CircleCheck /></el-icon>
            <p class="empty-text">未检测到目标</p>
            <p class="empty-desc">影像无异常目标</p>
          </div>
          <div v-else class="detection-list">
            <div
              v-for="(box, index) in activeDetectionResult.boxes"
              :key="index"
              class="detection-item"
            >
              <span class="item-name">{{ box.class_name }}</span>
              <span class="item-confidence"
                >{{ (box.confidence * 100).toFixed(1) }}%</span
              >
            </div>
          </div>
        </div>

        <!-- 批量检测结果 -->
        <div v-if="activeTab === 'batch' && batchResult" class="result-card">
          <div class="card-header">
            <el-icon><Grid /></el-icon>
            <span class="card-title">批量任务面板</span>
          </div>
          <el-progress
            :percentage="batchResult.progress || 0"
            :status="batchResult.status === 'failed' ? 'exception' : batchResult.status === 'completed' ? 'success' : undefined"
          />
          <div class="batch-summary">
            <div class="summary-item">
              <span class="summary-value">{{ batchResult.total }}</span>
              <span class="summary-label">总数</span>
            </div>
            <div class="summary-item success">
              <span class="summary-value">{{ batchResult.completed }}</span>
              <span class="summary-label">成功</span>
            </div>
            <div class="summary-item danger">
              <span class="summary-value">{{ batchResult.failed }}</span>
              <span class="summary-label">失败</span>
            </div>
          </div>
          <div class="batch-controls">
            <el-select v-model="batchFilter" size="small" class="batch-filter">
              <el-option label="全部" value="all" />
              <el-option label="成功" value="completed" />
              <el-option label="失败" value="failed" />
              <el-option label="处理中" value="processing" />
              <el-option label="待处理" value="pending" />
            </el-select>
            <el-button size="small" :disabled="!hasFailedItems" @click="handleRetryFailed">重试失败</el-button>
            <el-button size="small" :disabled="!canCancelBatch" @click="handleCancelBatch">取消</el-button>
            <el-dropdown @command="handleExportBatch">
              <el-button size="small">
                <el-icon><Download /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="json">JSON</el-dropdown-item>
                  <el-dropdown-item command="csv">CSV</el-dropdown-item>
                  <el-dropdown-item command="zip">ZIP</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
          <div class="batch-list">
            <div
              v-for="item in filteredBatchItems"
              :key="item.detection_id || item.filename"
              class="batch-item"
              :class="{ active: selectedBatchId === item.detection_id, failed: item.status === 'failed' }"
              @click="selectBatchItem(item)"
            >
              <div class="batch-item-main">
                <span class="batch-filename">{{ item.filename }}</span>
                <span class="batch-meta" v-if="item.result">
                  {{ item.result.total_objects }} 个目标 · {{ formatDetectionTime(item.result.detection_time) }}s
                </span>
                <span class="batch-meta" v-else>{{ item.error || item.message }}</span>
              </div>
              <el-tag size="small" :type="getBatchTagType(item.status)">
                {{ getBatchStatusText(item.status) }}
              </el-tag>
            </div>
          </div>
        </div>

        <!-- AI诊断建议 -->
        <div class="result-card">
          <div class="card-header">
            <el-icon><ChatDotRound /></el-icon>
            <span class="card-title">AI 诊断建议</span>
          </div>
          <div class="diagnosis-content">
            <p v-if="!hasDetectionContext">{{ diagnosisEmptyText }}</p>
            <p v-else-if="!activeDetectionResult">未检测到指定目标</p>
            <p v-else>
              检测到 {{ activeDetectionResult.total_objects }} 个目标，耗时
              {{ formatDetectionTime(activeDetectionResult.detection_time) }}s。 模型:
              {{ activeDetectionResult.model_name }}
            </p>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button
            size="default"
            class="btn-secondary"
            @click="handleRedetect"
          >
            <el-icon><Refresh /></el-icon>
            {{ resetButtonText }}
          </el-button>
          <el-button type="primary" size="default" class="btn-primary">
            查看完整报告
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { ElMessage, ElLoading, ElMessageBox } from "element-plus";
import {
  Picture,
  Plus,
  Monitor,
  Check,
  Grid,
  List,
  CircleCheck,
  ChatDotRound,
  Refresh,
  Upload,
  View,
  Delete,
  Download,
  VideoCamera,
} from "@element-plus/icons-vue";
import CameraDetection from "../components/CameraDetection.vue";
import VideoDetection from "../components/VideoDetection.vue";
import {
  cancelBatch,
  detectBatchImages,
  detectSingleImage,
  exportBatch,
  getBatchItems,
  getBatchStatus,
  getDetectionDetail,
  retryFailedBatch,
} from "../api/detection";

const selectedModel = ref("neu-det-yolo11n");
const route = useRoute();
const activeTab = ref("single");
const originalImage = ref(null);
const resultImage = ref(null);
const detectionResult = ref(null);
const isDetecting = ref(false);
const hasImage = ref(false);
const batchResult = ref(null);
const selectedBatchId = ref(null);
const batchFilter = ref("all");
const pendingBatchFiles = ref([]);
const cameraResult = ref(null);
const cameraRunning = ref(false);
const cameraDetectionRef = ref(null);
const videoResult = ref(null);
const videoRunning = ref(false);
const videoHasContext = ref(false);
const videoDetectionRef = ref(null);
let batchPollTimer = null;

const resultStatusText = computed(() => {
  if (isDetecting.value) return "检测中";
  if (activeTab.value === "camera") {
    if (cameraRunning.value) return "实时检测中";
    return cameraResult.value ? "检测已停止" : "等待开启";
  }
  if (activeTab.value === "video") {
    if (videoRunning.value) return "视频检测中";
    return videoResult.value ? "检测已停止" : "等待上传";
  }
  if (activeTab.value === "batch" && batchResult.value) {
    if (["pending", "processing"].includes(batchResult.value.status)) return "批量检测中";
    return batchResult.value.failed > 0 ? "部分完成" : "检测完成";
  }
  return hasImage.value && detectionResult.value ? "检测完成" : "等待上传";
});

const detectionModeText = computed(() => {
  if (activeTab.value === "batch") return "批量检测";
  if (activeTab.value === "camera") return "摄像头实时检测";
  if (activeTab.value === "video") return "视频检测";
  return "单图检测";
});

const activeDetectionResult = computed(() => {
  if (activeTab.value === "camera") return cameraResult.value;
  if (activeTab.value === "video") return videoResult.value;
  return detectionResult.value;
});

const hasDetectionContext = computed(() => {
  if (activeTab.value === "camera") return cameraRunning.value || Boolean(cameraResult.value);
  if (activeTab.value === "video") return videoHasContext.value || Boolean(videoResult.value);
  return hasImage.value;
});

const emptyStateText = computed(() => {
  if (activeTab.value === "camera") return "请开启摄像头";
  if (activeTab.value === "video") return "请上传视频";
  return "请上传图片开始检测";
});

const emptyStateDesc = computed(() => {
  if (activeTab.value === "camera") return "开启后实时识别画面目标";
  if (activeTab.value === "video") return "播放视频后实时识别缺陷目标";
  return "上传钢材表面图像以识别缺陷";
});

const diagnosisEmptyText = computed(() => {
  if (activeTab.value === "camera") return "开启摄像头后将实时更新检测结果";
  if (activeTab.value === "video") return "上传视频并开始检测后将实时更新检测结果";
  return "上传图片后将自动生成诊断建议";
});

const resetButtonText = computed(() => {
  if (activeTab.value === "camera") return "重置摄像头";
  if (activeTab.value === "video") return "停止视频";
  return "重新检测";
});

const filteredBatchItems = computed(() => {
  const items = batchResult.value?.items || [];
  if (batchFilter.value === "all") return items;
  return items.filter((item) => item.status === batchFilter.value);
});

const hasFailedItems = computed(() => {
  return (batchResult.value?.items || []).some((item) => item.status === "failed");
});

const canCancelBatch = computed(() => {
  return ["pending", "processing"].includes(batchResult.value?.status);
});

const functionTabs = [
  {
    key: "single",
    name: "单图检测",
    desc: "快速识别一张图片",
    icon: Picture,
    accept: "image/*",
    multiple: false,
  },
  {
    key: "batch",
    name: "批量检测",
    desc: "一次处理多张图片",
    icon: Plus,
    accept: "image/*",
    multiple: true,
  },
  {
    key: "camera",
    name: "摄像头",
    desc: "打开摄像头",
    icon: VideoCamera,
    accept: "image/*",
    multiple: false,
  },
  {
    key: "video",
    name: "视频检测",
    desc: "上传视频自动分析",
    icon: Monitor,
    accept: "video/*",
    multiple: false,
  },
];

const singleFileInputRef = ref(null);
const batchFileInputRef = ref(null);

const handleTabClick = (key) => {
  if (activeTab.value === "camera" && key !== "camera") {
    cameraDetectionRef.value?.stopCamera();
  }
  if (activeTab.value === "video" && key !== "video") {
    videoDetectionRef.value?.stopDetection();
  }
  activeTab.value = key;
  if (key === "camera") {
    stopBatchPolling();
    isDetecting.value = false;
    batchResult.value = null;
    pendingBatchFiles.value = [];
    detectionResult.value = null;
    originalImage.value = null;
    resultImage.value = null;
    hasImage.value = false;
  }
  if (key === "video") {
    stopBatchPolling();
    cameraDetectionRef.value?.stopCamera();
    isDetecting.value = false;
    batchResult.value = null;
    pendingBatchFiles.value = [];
    detectionResult.value = null;
    originalImage.value = null;
    resultImage.value = null;
    hasImage.value = false;
  }
};

const handleCameraResult = (result) => {
  cameraResult.value = result;
};

const handleCameraRunningChange = (running) => {
  cameraRunning.value = running;
};

const handleVideoResult = (result) => {
  videoResult.value = result;
};

const handleVideoRunningChange = (running) => {
  videoRunning.value = running;
};

const handleVideoContextChange = (hasContext) => {
  videoHasContext.value = hasContext;
};

const triggerBatchFileInput = () => {
  if (batchFileInputRef.value) {
    batchFileInputRef.value.click();
  }
};

const handleFileChange = async (event, tabKey) => {
  event.stopPropagation();
  event.preventDefault();
  const files = event.target.files;
  if (files && files.length > 0) {
    if (tabKey === "single") {
      await performSingleDetection(files[0]);
    } else if (tabKey === "batch") {
      pendingBatchFiles.value = Array.from(files);
    }
  }
  setTimeout(() => {
    event.target.value = "";
  }, 0);
};

const performSingleDetection = async (file) => {
  const loading = ElLoading.service({
    lock: true,
    text: "正在检测中...",
    background: "rgba(0, 0, 0, 0.7)",
  });

  try {
    isDetecting.value = true;
    hasImage.value = true;
    batchResult.value = null;
    selectedBatchId.value = null;
    detectionResult.value = null;
    resultImage.value = null;

    const formData = new FormData();
    formData.append("file", file);
    formData.append("model_name", selectedModel.value);

    originalImage.value = URL.createObjectURL(file);

    const response = await detectSingleImage(formData);
    if (response.success && response.data) {
      detectionResult.value = response.data;
      resultImage.value = response.data.result_image_url;
      ElMessage.success("检测成功！");
    } else {
      ElMessage.error(response.message || "检测失败");
    }
  } catch (error) {
    console.error("检测错误:", error);
    ElMessage.error("检测失败，请稍后重试");
  } finally {
    isDetecting.value = false;
    loading.close();
  }
};

const performBatchDetection = async (files) => {
  if (files.length === 0) return;
  if (files.length > 20) {
    ElMessage.warning("单次最多支持 20 张图片");
    return;
  }

  try {
    isDetecting.value = true;
    hasImage.value = true;
    detectionResult.value = null;
    resultImage.value = null;
    originalImage.value = URL.createObjectURL(files[0]);
    batchResult.value = null;
    selectedBatchId.value = null;

    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file);
    });
    formData.append("model_name", selectedModel.value);

    const response = await detectBatchImages(formData);
    if (response.data) {
      batchResult.value = response.data;
      ElMessage.success(response.message || "批量检测任务已创建");
      startBatchPolling(response.data.batch_id);
    } else {
      ElMessage.error(response.message || "批量检测失败");
    }
  } catch (error) {
    console.error("批量检测错误:", error);
    ElMessage.error("批量检测失败，请稍后重试");
  } finally {
    pendingBatchFiles.value = [];
  }
};

const startPendingBatch = async () => {
  await performBatchDetection(pendingBatchFiles.value);
};

const removePendingFile = (index) => {
  pendingBatchFiles.value.splice(index, 1);
};

const startBatchPolling = (batchId) => {
  stopBatchPolling();
  refreshBatch(batchId);
  batchPollTimer = window.setInterval(() => refreshBatch(batchId), 2000);
};

const stopBatchPolling = () => {
  if (batchPollTimer) {
    window.clearInterval(batchPollTimer);
    batchPollTimer = null;
  }
};

const refreshBatch = async (batchId) => {
  try {
    const [statusResponse, itemsResponse] = await Promise.all([
      getBatchStatus(batchId),
      getBatchItems(batchId),
    ]);
    if (statusResponse.data) {
      batchResult.value = {
        ...statusResponse.data,
        items: itemsResponse.data?.items || batchResult.value?.items || [],
      };
      const firstCompleted = batchResult.value.items.find(
        (item) => item.status === "completed" && item.result,
      );
      if (!selectedBatchId.value && firstCompleted) {
        selectBatchItem(firstCompleted);
      }
      if (!["pending", "processing"].includes(batchResult.value.status)) {
        isDetecting.value = false;
        stopBatchPolling();
      }
    }
  } catch (error) {
    console.error("刷新批量任务失败:", error);
  }
};

const selectBatchItem = (item) => {
  if (!item) return;
  selectedBatchId.value = item.detection_id;
  if (item.result) {
    detectionResult.value = item.result;
    originalImage.value = item.result.image_url;
    resultImage.value = item.result.result_image_url;
    hasImage.value = true;
  } else {
    detectionResult.value = null;
    originalImage.value = null;
    resultImage.value = null;
    hasImage.value = false;
  }
};

const loadDetectionDetail = async (detectionId) => {
  if (!detectionId) return;

  stopBatchPolling();
  activeTab.value = "single";
  isDetecting.value = true;
  batchResult.value = null;
  selectedBatchId.value = null;
  detectionResult.value = null;
  originalImage.value = null;
  resultImage.value = null;
  hasImage.value = false;

  try {
    const response = await getDetectionDetail(detectionId);
    if (response.success && response.data) {
      detectionResult.value = response.data;
      originalImage.value = response.data.image_url;
      resultImage.value = response.data.result_image_url;
      selectedModel.value = response.data.model_name || selectedModel.value;
      hasImage.value = Boolean(response.data.image_url || response.data.result_image_url);
    } else {
      ElMessage.error(response.message || "获取检测详情失败");
    }
  } catch (error) {
    console.error("获取检测详情失败:", error);
  } finally {
    isDetecting.value = false;
  }
};

const loadRouteResult = () => {
  if (activeTab.value === "camera") {
    cameraDetectionRef.value?.stopCamera();
  }
  const batchId = route.query.batch_id;
  const detectionId = route.query.detection_id;

  if (batchId) {
    activeTab.value = "batch";
    hasImage.value = true;
    isDetecting.value = true;
    detectionResult.value = null;
    originalImage.value = null;
    resultImage.value = null;
    startBatchPolling(batchId);
    return;
  }

  if (detectionId) {
    loadDetectionDetail(detectionId);
  }
};

const getBatchStatusText = (status) => {
  const texts = {
    pending: "待处理",
    processing: "处理中",
    completed: "成功",
    failed: "失败",
    partial_failed: "部分失败",
    cancelled: "已取消",
  };
  return texts[status] || status;
};

const getBatchTagType = (status) => {
  if (status === "completed") return "success";
  if (status === "failed") return "danger";
  if (status === "processing") return "warning";
  return "info";
};

const handleRetryFailed = async () => {
  if (!batchResult.value?.batch_id) return;
  await retryFailedBatch(batchResult.value.batch_id);
  isDetecting.value = true;
  startBatchPolling(batchResult.value.batch_id);
};

const handleCancelBatch = async () => {
  if (!batchResult.value?.batch_id) return;
  await ElMessageBox.confirm("确定取消当前批量任务吗？", "取消任务", {
    confirmButtonText: "确定",
    cancelButtonText: "返回",
    type: "warning",
  });
  await cancelBatch(batchResult.value.batch_id);
  await refreshBatch(batchResult.value.batch_id);
};

const handleExportBatch = async (type) => {
  if (!batchResult.value?.batch_id) return;
  const blob = await exportBatch(batchResult.value.batch_id, type);
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `batch_${batchResult.value.batch_id}.${type}`;
  link.click();
  window.URL.revokeObjectURL(url);
};

const formatFileSize = (size) => {
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / 1024 / 1024).toFixed(1)} MB`;
};

const formatDetectionTime = (time) => {
  const value = Number(time);
  return Number.isFinite(value) ? value.toFixed(3) : "0.000";
};

const handleRedetect = () => {
  if (activeTab.value === "camera") {
    cameraDetectionRef.value?.stopCamera();
    cameraResult.value = null;
    cameraRunning.value = false;
    return;
  }
  if (activeTab.value === "batch") {
    triggerBatchFileInput();
    return;
  }
  if (activeTab.value === "video") {
    videoDetectionRef.value?.stopDetection();
    return;
  }
  // 单图检测：重置为初始状态
  detectionResult.value = null;
  originalImage.value = null;
  resultImage.value = null;
  hasImage.value = false;
};

onBeforeUnmount(() => {
  stopBatchPolling();
  cameraDetectionRef.value?.stopCamera();
  videoDetectionRef.value?.stopDetection();
});

onMounted(() => {
  loadRouteResult();
});

watch(
  () => [route.query.batch_id, route.query.detection_id],
  () => {
    loadRouteResult();
  },
);
</script>

<style scoped>
.detection-page {
  width: 100%;
  position: relative;
  animation: fadeIn 0.3s ease-out;
}

.page-header {
  margin-bottom: 32px;
  padding-top: 0;
}

.breadcrumb {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.separator {
  margin: 0 6px;
  color: var(--text-tertiary);
}

.active {
  color: var(--text-primary);
  font-weight: 500;
}

.page-title {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
  letter-spacing: -0.02em;
}

.page-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
}

.model-selector {
  position: absolute;
  top: 0;
  right: 0;
  z-index: 10;
}

/* 功能选项卡 */
.function-tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.function-tab {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 16px 20px;
  background-color: var(--bg-primary);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  border: 2px solid transparent;
  position: relative;
  overflow: hidden;
  box-shadow: var(--card-shadow);
}

.single-file-input {
  position: absolute;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  z-index: 10;
}

.function-tab:hover {
  background-color: var(--primary-light);
  box-shadow: var(--card-shadow-hover);
  transform: translateY(-2px);
}

.function-tab.active {
  background: linear-gradient(135deg, var(--primary-light) 0%, rgba(59, 130, 246, 0.06) 100%);
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

/* 批量检测上传区域 */
.batch-upload-area {
  margin-bottom: 24px;
}

.batch-upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  background-color: var(--bg-primary);
  border: 2px dashed var(--border-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  position: relative;
  overflow: hidden;
}

.batch-upload-placeholder:hover {
  border-color: var(--primary-color);
  background-color: var(--primary-light);
}

.batch-file-input {
  position: absolute;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  z-index: 10;
}

.batch-upload-icon {
  font-size: 48px;
  color: var(--text-tertiary);
  margin-bottom: 16px;
}

.batch-upload-placeholder:hover .batch-upload-icon {
  color: var(--primary-color);
}

.batch-upload-text {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.batch-upload-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 20px;
}

.batch-upload-btn {
  z-index: 20;
  position: relative;
}

.upload-panel {
  background-color: var(--bg-primary);
  border-radius: var(--radius-md);
  padding: 16px;
  margin-bottom: 24px;
  box-shadow: var(--card-shadow);
}

.upload-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 12px;
}

.panel-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.upload-count {
  margin-left: 10px;
  font-size: 13px;
  color: var(--text-secondary);
}

.upload-actions {
  display: flex;
  gap: 8px;
}

.upload-file-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 8px;
}

.upload-file {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto 28px;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  background-color: var(--bg-tertiary);
  border-radius: var(--radius-sm);
}

.upload-file-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
  color: var(--text-primary);
}

.upload-file-size {
  font-size: 12px;
  color: var(--text-secondary);
}

.tab-icon {
  font-size: 18px;
  color: var(--primary-color);
  margin-right: 12px;
  flex-shrink: 0;
}

.tab-content {
  display: flex;
  flex-direction: column;
}

.tab-text {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.4;
}

.tab-desc {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.4;
}

/* 主内容区域 */
.main-content {
  display: flex;
  gap: 24px;
}

.left-panel {
  flex: 1;
  background-color: var(--bg-primary);
  border-radius: var(--radius-md);
  padding: 20px;
  box-shadow: var(--card-shadow);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.result-tag {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
}

/* 图片对比区域 */
.image-compare {
  display: flex;
  gap: 16px;
  height: 320px;
}

.image-card {
  flex: 1;
  position: relative;
  border-radius: var(--radius-sm);
  overflow: hidden;
  background-color: var(--bg-tertiary);
}

.image-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  width: 100%;
  padding: 24px;
  text-align: center;
}

.placeholder-icon {
  font-size: 48px;
  color: var(--border-color);
  margin-bottom: 12px;
}

.placeholder-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.placeholder-desc {
  font-size: 12px;
  color: var(--text-tertiary);
}

.compare-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.image-label {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  color: #ffffff;
  font-size: 13px;
  font-weight: 500;
}

.detection-mark {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: var(--success-color);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
}

.detection-mark::after {
  content: "✓";
  color: #ffffff;
  font-size: 18px;
  font-weight: bold;
}

/* 右侧面板 */
.right-panel {
  width: 360px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-card {
  background-color: var(--bg-primary);
  border-radius: var(--radius-md);
  padding: 16px;
  box-shadow: var(--card-shadow);
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-light);
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.info-value {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.result-card {
  background-color: var(--bg-primary);
  border-radius: var(--radius-md);
  padding: 16px;
  box-shadow: var(--card-shadow);
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.card-header .el-icon {
  font-size: 16px;
  color: var(--primary-color);
  margin-right: 8px;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 0;
}

.empty-icon {
  font-size: 48px;
  color: var(--success-color);
  margin-bottom: 12px;
}

.empty-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.empty-desc {
  font-size: 13px;
  color: var(--text-secondary);
}

.diagnosis-content {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.detection-list {
  max-height: 200px;
  overflow-y: auto;
}

.detection-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background-color: var(--bg-tertiary);
  border-radius: var(--radius-sm);
  margin-bottom: 8px;
  transition: all var(--transition-fast);
}

.detection-item:hover {
  background-color: var(--primary-light);
}

.detection-item:last-child {
  margin-bottom: 0;
}

.batch-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin: 12px 0;
}

.batch-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.batch-filter {
  width: 94px;
  flex-shrink: 0;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 6px;
  background-color: var(--bg-tertiary);
  border-radius: var(--radius-sm);
}

.summary-item.success .summary-value {
  color: var(--success-color);
}

.summary-item.danger .summary-value {
  color: var(--danger-color);
}

.summary-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.summary-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.batch-list {
  max-height: 260px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.batch-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 10px 12px;
  background-color: var(--bg-tertiary);
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.batch-item:hover,
.batch-item.active {
  border-color: var(--primary-color);
  background-color: var(--primary-light);
}

.batch-item.failed {
  cursor: default;
}

.batch-item-main {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.batch-filename {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.batch-meta {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 12px;
  color: var(--text-secondary);
}

.item-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.item-confidence {
  font-size: 12px;
  color: var(--primary-color);
  font-weight: 600;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.btn-secondary {
  flex: 1;
  border-radius: var(--radius-sm);
  padding: 10px;
  font-size: 14px;
}

.btn-primary {
  flex: 2;
  border-radius: var(--radius-sm);
  padding: 10px;
  font-size: 14px;
  background: var(--primary-gradient);
  border: none;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}
</style>
