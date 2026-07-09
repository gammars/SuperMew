<template>
  <div class="input-area-wrapper" ref="inputWrapperRef">
    <div v-if="documentPanelOpen" class="document-scope-popover">
      <div class="document-scope-popover-header">
        <div>
          <div class="document-scope-title">指定检索文档</div>
          <div class="document-scope-subtitle">{{ scopeLabel }}</div>
        </div>
        <button
          class="scope-clear-btn"
          type="button"
          :disabled="chatStore.selectedDocuments.length === 0"
          @click="chatStore.clearSelectedDocuments"
        >
          全部文档
        </button>
      </div>

      <div v-if="documentStore.documents.length" class="document-list-popover">
        <button
          v-for="doc in documentStore.documents"
          :key="doc.filename"
          type="button"
          class="document-list-item"
          :class="{ active: chatStore.selectedDocuments.includes(doc.filename) }"
          :title="doc.filename"
          @click="chatStore.toggleSelectedDocument(doc.filename)"
        >
          <span class="document-check">
            <i class="fas fa-check"></i>
          </span>
          <span class="document-list-name">{{ doc.filename }}</span>
          <span class="document-list-meta">{{ doc.chunk_count }} chunks</span>
        </button>
      </div>

      <div v-else class="empty-document-list">
        <span>{{ documentStore.documentsLoading ? '正在加载文档列表...' : '还没有可选文档' }}</span>
        <button
          class="scope-clear-btn"
          type="button"
          :disabled="documentStore.documentsLoading"
          @click="loadDocumentsSilently"
        >
          刷新
        </button>
      </div>
    </div>

    <div class="input-area">
      <button
        class="attach-btn"
        :class="{ active: documentPanelOpen || chatStore.selectedDocuments.length > 0 }"
        type="button"
        :title="scopeLabel"
        @click="toggleDocumentPanel"
      >
        <i class="fas fa-paperclip"></i>
        <span v-if="chatStore.selectedDocuments.length" class="attach-badge">
          {{ chatStore.selectedDocuments.length }}
        </span>
      </button>

      <textarea
        v-model="chatStore.userInput"
        @keydown="handleKeyDown"
        @compositionstart="handleCompositionStart"
        @compositionend="handleCompositionEnd"
        @input="autoResize"
        placeholder="和喵喵说点什么吧... (Shift+Enter 换行)"
        rows="1"
        ref="textareaRef"
      ></textarea>

      <button
        v-if="chatStore.isLoading"
        @click="chatStore.handleStop"
        class="send-btn stop-btn"
        title="终止回答"
      >
        <i class="fas fa-stop"></i>
      </button>

      <button
        v-else
        @click="onSend"
        class="send-btn"
        title="发送"
      >
        <i class="fas fa-paper-plane"></i>
      </button>
    </div>
    <div class="footer-text">AI 生成的内容可能包含错误，请仔细甄别。</div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue';
import { useChatStore } from '@/stores/chat';
import { useDocumentStore } from '@/stores/documents';

const chatStore = useChatStore();
const documentStore = useDocumentStore();
const textareaRef = ref<HTMLTextAreaElement | null>(null);
const inputWrapperRef = ref<HTMLElement | null>(null);
const isComposing = ref(false);
const documentPanelOpen = ref(false);

const scopeLabel = computed(() => {
  const count = chatStore.selectedDocuments.length;
  if (count === 0) {
    return '检索范围：全部已上传文档';
  }
  if (count === 1) {
    return `检索范围：${chatStore.selectedDocuments[0]}`;
  }
  return `检索范围：已指定 ${count} 个文档`;
});

const loadDocumentsSilently = async () => {
  try {
    await documentStore.loadDocuments();
  } catch (error) {
    console.warn('加载文档列表失败:', error);
  }
};

const toggleDocumentPanel = async () => {
  documentPanelOpen.value = !documentPanelOpen.value;
  if (documentPanelOpen.value && !documentStore.documents.length) {
    await loadDocumentsSilently();
  }
};

const handleOutsideClick = (event: MouseEvent) => {
  if (!documentPanelOpen.value) return;
  const target = event.target as Node | null;
  if (target && inputWrapperRef.value?.contains(target)) return;
  documentPanelOpen.value = false;
};

onMounted(() => {
  document.addEventListener('click', handleOutsideClick);
});

onBeforeUnmount(() => {
  document.removeEventListener('click', handleOutsideClick);
});

const handleCompositionStart = () => {
  isComposing.value = true;
};

const handleCompositionEnd = () => {
  isComposing.value = false;
};

const handleKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey && !isComposing.value) {
    event.preventDefault();
    onSend();
  }
};

const autoResize = () => {
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto';
    textareaRef.value.style.height = textareaRef.value.scrollHeight + 'px';
  }
};

const resetTextareaHeight = () => {
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto';
  }
};

const onSend = async () => {
  const text = chatStore.userInput.trim();
  if (!text || chatStore.isLoading || isComposing.value) return;

  documentPanelOpen.value = false;
  await chatStore.handleSend();

  await nextTick();
  resetTextareaHeight();
};
</script>
