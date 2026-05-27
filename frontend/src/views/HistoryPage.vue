<template>
  <div class="history-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">检测历史记录</h1>
      <p class="page-subtitle">查看和管理您的所有检测记录</p>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-bar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索检测记录..."
        size="default"
        class="search-input"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <el-select
        v-model="filterStatus"
        placeholder="状态筛选"
        size="default"
        class="filter-select"
      >
        <el-option label="全部" value="" />
        <el-option label="检测完成" value="completed" />
        <el-option label="检测中" value="processing" />
        <el-option label="失败" value="failed" />
      </el-select>

      <el-select
        v-model="filterType"
        placeholder="类型筛选"
        size="default"
        class="filter-select"
      >
        <el-option label="全部" value="" />
        <el-option label="单图检测" value="single" />
        <el-option label="批量检测" value="batch" />
        <el-option label="文件夹" value="folder" />
        <el-option label="视频检测" value="video" />
      </el-select>
    </div>

    <!-- 记录列表 -->
    <div class="history-list">
      <div
        v-for="record in filteredRecords"
        :key="record.id"
        class="history-card"
        @click="viewRecord(record)"
      >
        <div class="record-preview">
          <img
            :src="record.result_image_url || record.image_url"
            :alt="record.filename"
            class="preview-image"
          />
          <div
            class="status-badge"
            :class="record.status"
          >
            <el-icon><component :is="getStatusIcon(record.status)" /></el-icon>
            {{ getStatusText(record.status) }}
          </div>
        </div>

        <div class="record-info">
          <div class="record-header">
            <span class="record-filename">{{ record.filename }}</span>
            <span class="record-type">{{ getTypeText(record.type) }}</span>
          </div>
          <div class="record-meta">
            <span class="meta-item">
              <el-icon><Clock /></el-icon>
              {{ record.time }}
            </span>
            <span class="meta-item">
              <el-icon><Picture /></el-icon>
              {{ record.count || 1 }} 张图片
            </span>
            <span class="meta-item">
              <el-icon><Aim /></el-icon>
              {{ record.total_objects }} 个目标
            </span>
          </div>
          <div class="record-tags">
            <span
              v-for="tag in record.detectedTargets"
              :key="tag"
              class="detected-tag"
            >
              {{ tag }}
            </span>
          </div>
        </div>

        <div class="record-actions">
          <el-button size="small" @click.stop="viewRecord(record)">
            <el-icon><Monitor/></el-icon>
            查看
          </el-button>
          <el-dropdown
            trigger="click"
            @command="downloadRecord"
            @click.stop
          >
            <el-button size="small" @click.stop>
              <el-icon><Download/></el-icon>
              下载
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <template v-if="record.type === 'batch'">
                  <el-dropdown-item :command="{ record, action: 'batch-select' }">
                    选择图片下载
                  </el-dropdown-item>
                  <el-dropdown-item :command="{ record, action: 'batch-zip' }">
                    下载全部压缩包
                  </el-dropdown-item>
                </template>
                <template v-else>
                  <el-dropdown-item
                    :command="{ record, type: 'original' }"
                    :disabled="!record.image_url"
                  >
                    下载原图
                  </el-dropdown-item>
                  <el-dropdown-item
                    :command="{ record, type: 'result' }"
                    :disabled="!record.result_image_url"
                  >
                    下载检测结果图
                  </el-dropdown-item>
                </template>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <el-button
            size="small"
            type="danger"
            @click.stop="deleteRecord(record)"
          >
            <el-icon><Delete/></el-icon>
            删除
          </el-button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="filteredRecords.length === 0" class="empty-state">
      <el-icon :size="64" class="empty-icon"><Help /></el-icon>
      <p class="empty-text">暂无检测记录</p>
      <el-button type="primary" @click="goToDetection">
        <el-icon><Plus /></el-icon>
        开始检测
      </el-button>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <el-pagination
        v-if="totalRecords > 0"
        :total="totalRecords"
        :page-size="pageSize"
        :current-page="currentPage"
        @current-change="handlePageChange"
        layout="prev, pager, next"
      />
    </div>

    <el-dialog
      v-model="batchDownloadVisible"
      title="选择批量任务图片"
      width="680px"
      class="batch-download-dialog"
    >
      <div class="batch-download-toolbar">
        <el-radio-group v-model="batchDownloadType" size="small">
          <el-radio-button label="result">检测结果图</el-radio-button>
          <el-radio-button label="original">原图</el-radio-button>
          <el-radio-button label="both">原图和结果图</el-radio-button>
        </el-radio-group>
        <el-button size="small" @click="selectAllBatchDownloads">全选可下载</el-button>
      </div>

      <el-skeleton v-if="batchDownloadLoading" :rows="5" animated />
      <el-checkbox-group
        v-else
        v-model="selectedBatchDownloadIds"
        class="batch-download-list"
      >
        <div
          v-for="item in batchDownloadItems"
          :key="getBatchItemId(item)"
          class="batch-download-item"
          :class="{ disabled: !canDownloadBatchItem(item) }"
        >
          <el-checkbox
            :label="getBatchItemId(item)"
            :disabled="!canDownloadBatchItem(item)"
          >
            <span class="batch-download-name">{{ item.filename }}</span>
          </el-checkbox>
          <el-tag size="small" :type="item.status === 'completed' ? 'success' : 'info'">
            {{ getStatusText(item.status) }}
          </el-tag>
        </div>
      </el-checkbox-group>

      <template #footer>
        <el-button @click="batchDownloadVisible = false">取消</el-button>
        <el-button
          type="primary"
          :disabled="selectedBatchDownloadIds.length === 0"
          @click="downloadSelectedBatchImages"
        >
          下载选中图片
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import {
  Search,
  Clock,
  Picture,
  Aim,
  Monitor,
  Download,
  Delete,
  Plus,
  Help,
  CircleCheck,
  Loading,
  CircleClose,
} from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  deleteDetection,
  exportBatch,
  getBatchItems,
  getDetectionHistory,
} from "../api/detection";

const router = useRouter();

const searchQuery = ref("");
const filterStatus = ref("");
const filterType = ref("");
const currentPage = ref(1);
const pageSize = ref(10);
const isLoading = ref(false);

const historyRecords = ref([]);
const totalRecords = ref(0);
const batchDownloadVisible = ref(false);
const batchDownloadLoading = ref(false);
const batchDownloadItems = ref([]);
const selectedBatchDownloadIds = ref([]);
const selectedBatchRecord = ref(null);
const batchDownloadType = ref("result");

const fetchHistory = async () => {
  isLoading.value = true;
  try {
    const response = await getDetectionHistory({
      page: currentPage.value,
      page_size: pageSize.value,
    });
    if (response.success && response.data) {
      historyRecords.value = response.data;
      totalRecords.value = response.total;
    }
  } catch (error) {
    console.error("获取历史记录失败:", error);
    historyRecords.value = [];
    totalRecords.value = 0;
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchHistory();
});

const filteredRecords = computed(() => {
  return historyRecords.value.filter((record) => {
    const matchesSearch =
      !searchQuery.value ||
      record.filename.toLowerCase().includes(searchQuery.value.toLowerCase());
    const matchesStatus = !filterStatus.value || record.status === filterStatus.value;
    const matchesType = !filterType.value || record.type === filterType.value;
    return matchesSearch && matchesStatus && matchesType;
  });
});

watch(batchDownloadType, () => {
  const selectedIds = new Set(selectedBatchDownloadIds.value);
  selectedBatchDownloadIds.value = batchDownloadItems.value
    .filter((item) => selectedIds.has(getBatchItemId(item)) && canDownloadBatchItem(item))
    .map(getBatchItemId);
});

const getStatusIcon = (status) => {
  const icons = {
    completed: CircleCheck,
    processing: Loading,
    failed: CircleClose,
  };
  return icons[status] || CircleCheck;
};

const getStatusText = (status) => {
  const texts = {
    completed: "检测完成",
    processing: "检测中",
    failed: "失败",
  };
  return texts[status] || status;
};

const getTypeText = (type) => {
  const texts = {
    single: "单图检测",
    batch: "批量检测",
    folder: "文件夹",
    video: "视频检测",
  };
  return texts[type] || type;
};

const viewRecord = (record) => {
  if (record.type === "batch") {
    router.push({ path: "/detection", query: { batch_id: record.id } });
    return;
  }
  router.push({ path: "/detection", query: { detection_id: record.id } });
};

const getDownloadFilename = (record, type, url, filename) => {
  const prefix = type === "original" ? "original" : "result";
  const fallbackName = `${prefix}_${filename || record.filename || record.id || "image"}.jpg`;

  try {
    const pathname = new URL(url).pathname;
    const urlFilename = decodeURIComponent(pathname.split("/").pop() || fallbackName);
    return type === "original" ? urlFilename : `${prefix}_${urlFilename}`;
  } catch {
    return fallbackName;
  }
};

const triggerBlobDownload = (blob, filename) => {
  const objectUrl = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = objectUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(objectUrl);
};

const downloadUrl = async (url, filename) => {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  const blob = await response.blob();
  triggerBlobDownload(blob, filename);
};

const getBatchItemId = (item) => item.detection_id || item.filename;

const getBatchItemUrls = (item) => ({
  original: item.result?.image_url,
  result: item.result?.result_image_url,
});

const canDownloadBatchItem = (item) => {
  const urls = getBatchItemUrls(item);
  if (batchDownloadType.value === "both") {
    return Boolean(urls.original || urls.result);
  }
  return Boolean(urls[batchDownloadType.value]);
};

const selectAllBatchDownloads = () => {
  selectedBatchDownloadIds.value = batchDownloadItems.value
    .filter(canDownloadBatchItem)
    .map(getBatchItemId);
};

const openBatchDownloadDialog = async (record) => {
  selectedBatchRecord.value = record;
  batchDownloadVisible.value = true;
  batchDownloadLoading.value = true;
  batchDownloadItems.value = [];
  selectedBatchDownloadIds.value = [];
  batchDownloadType.value = "result";

  try {
    const response = await getBatchItems(record.id);
    batchDownloadItems.value = response.data?.items || [];
    selectAllBatchDownloads();
  } catch (error) {
    console.error("获取批量任务图片失败:", error);
    ElMessage.error("获取批量任务图片失败");
  } finally {
    batchDownloadLoading.value = false;
  }
};

const downloadBatchZip = async (record) => {
  try {
    const blob = await exportBatch(record.id, "zip");
    triggerBlobDownload(blob, `batch_${record.id}.zip`);
  } catch (error) {
    console.error("下载批量压缩包失败:", error);
    ElMessage.error("下载失败，请稍后重试");
  }
};

const downloadSelectedBatchImages = async () => {
  const record = selectedBatchRecord.value;
  if (!record) return;

  const selectedIds = new Set(selectedBatchDownloadIds.value);
  const selectedItems = batchDownloadItems.value.filter((item) =>
    selectedIds.has(getBatchItemId(item)),
  );

  try {
    for (const item of selectedItems) {
      const urls = getBatchItemUrls(item);
      const downloads = batchDownloadType.value === "both"
        ? ["original", "result"]
        : [batchDownloadType.value];

      for (const type of downloads) {
        if (!urls[type]) continue;
        await downloadUrl(
          urls[type],
          getDownloadFilename(record, type, urls[type], item.filename),
        );
      }
    }
    ElMessage.success("已开始下载选中图片");
    batchDownloadVisible.value = false;
  } catch (error) {
    console.error("下载批量图片失败:", error);
    ElMessage.error("部分图片下载失败，请稍后重试");
  }
};

const downloadRecord = async ({ record, type, action }) => {
  if (action === "batch-select") {
    await openBatchDownloadDialog(record);
    return;
  }

  if (action === "batch-zip") {
    await downloadBatchZip(record);
    return;
  }

  const url = type === "original" ? record.image_url : record.result_image_url;
  if (!url) {
    ElMessage.warning(type === "original" ? "原图不存在" : "检测结果图不存在");
    return;
  }

  try {
    await downloadUrl(url, getDownloadFilename(record, type, url));
  } catch (error) {
    console.error("下载图片失败:", error);
    ElMessage.error("下载失败，请稍后重试");
  }
};

const deleteRecord = async (record) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除记录 "${record.filename}" 吗？删除后不可恢复。`,
      "确认删除",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    );
    await deleteDetection(record.id);
    const index = historyRecords.value.findIndex((r) => r.id === record.id);
    if (index > -1) {
      historyRecords.value.splice(index, 1);
    }
    totalRecords.value -= 1;
    ElMessage.success("删除成功");
  } catch (error) {
    if (error !== "cancel") {
      console.error("删除检测记录失败:", error);
      ElMessage.error("删除失败，请稍后重试");
    }
  }
};

const goToDetection = () => {
  router.push("/detection");
};

const handlePageChange = (page) => {
  currentPage.value = page;
};
</script>

<style scoped>
.history-page {
  width: 100%;
  animation: fadeIn 0.3s ease-out;
}

.page-header {
  margin-bottom: 24px;
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

.search-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  align-items: center;
}

.search-input {
  flex: 1;
  max-width: 300px;
}

.filter-select {
  width: 140px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.history-card {
  background-color: var(--bg-primary);
  border-radius: var(--radius-md);
  padding: 20px;
  box-shadow: var(--card-shadow);
  display: flex;
  align-items: center;
  gap: 20px;
  cursor: pointer;
  transition: all var(--transition-fast);
  border: 1px solid var(--border-light);
}

.history-card:hover {
  box-shadow: var(--card-shadow-hover);
  transform: translateY(-2px);
  border-color: var(--primary-color);
}

.record-preview {
  position: relative;
  width: 120px;
  height: 80px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  flex-shrink: 0;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.status-badge {
  position: absolute;
  bottom: 8px;
  left: 8px;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
  backdrop-filter: blur(4px);
}

.status-badge.completed {
  background-color: rgba(16, 185, 129, 0.9);
  color: white;
}

.status-badge.processing {
  background-color: rgba(59, 130, 246, 0.9);
  color: white;
}

.status-badge.failed {
  background-color: rgba(239, 68, 68, 0.9);
  color: white;
}

.record-info {
  flex: 1;
  min-width: 0;
}

.record-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.record-filename {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.record-type {
  padding: 3px 10px;
  background-color: var(--bg-tertiary);
  border-radius: var(--radius-sm);
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

.record-meta {
  display: flex;
  gap: 20px;
  margin-bottom: 10px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--text-secondary);
}

.record-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.detected-tag {
  padding: 3px 10px;
  background-color: var(--success-light);
  color: var(--success-color);
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 500;
}

.record-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
}

.empty-icon {
  color: var(--text-tertiary);
  margin-bottom: 16px;
}

.empty-text {
  font-size: 15px;
  color: var(--text-secondary);
  margin-bottom: 24px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}

.batch-download-dialog :deep(.el-dialog__body) {
  padding: 20px;
}

.batch-download-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.batch-download-list {
  max-height: 360px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.batch-download-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-sm);
}

.batch-download-item.disabled {
  opacity: 0.55;
}

.batch-download-name {
  display: inline-block;
  max-width: 460px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  vertical-align: middle;
  font-size: 13px;
  font-weight: 500;
}
</style>
