<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title class="text-h5">
            <v-icon left>mdi-robot</v-icon>
            大模型配置
          </v-card-title>
          <v-card-subtitle>
            配置您的AI大模型接口信息
          </v-card-subtitle>

          <v-card-text>
            <v-form ref="form" v-model="valid">
              <v-select
                v-model="selectedModel"
                :items="modelOptions"
                item-title="name"
                item-value="value"
                label="选择模型提供商"
                prepend-icon="mdi-cloud"
                @update:model-value="onModelChange"
                required
                class="mb-4"
              ></v-select>

              <v-text-field
                v-model="config.apiKey"
                label="API Key"
                prepend-icon="mdi-key"
                :type="showApiKey ? 'text' : 'password'"
                :append-inner-icon="showApiKey ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append-inner="showApiKey = !showApiKey"
                :rules="apiKeyRules"
                required
                class="mb-4"
              ></v-text-field>

              <v-text-field
                v-model="config.baseUrl"
                label="API 基础地址"
                prepend-icon="mdi-web"
                :rules="urlRules"
                required
                class="mb-4"
              ></v-text-field>

              <v-text-field
                v-model="config.model"
                label="模型名称"
                prepend-icon="mdi-brain"
                :rules="modelRules"
                required
                class="mb-4"
              ></v-text-field>

              <v-slider
                v-model="config.temperature"
                label="Temperature"
                min="0"
                max="2"
                step="0.1"
                thumb-label
                prepend-icon="mdi-thermometer"
                class="mb-4"
              ></v-slider>

              <v-slider
                v-model="config.maxTokens"
                label="Max Tokens"
                min="100"
                max="4000"
                step="100"
                thumb-label
                prepend-icon="mdi-text-long"
                class="mb-4"
              ></v-slider>

              <v-card class="mb-4" outlined>
                <v-card-title class="text-subtitle-1">
                  <v-icon left>mdi-test-tube</v-icon>
                  测试配置
                </v-card-title>
                <v-card-text>
                  <v-textarea
                    v-model="testMessage"
                    label="测试消息"
                    rows="3"
                    placeholder="输入一条测试消息来验证配置是否正确"
                    class="mb-2"
                  ></v-textarea>
                  <v-btn
                    @click="testConnection"
                    :loading="testing"
                    :disabled="!valid || !testMessage"
                    color="info"
                    variant="outlined"
                  >
                    <v-icon left>mdi-lightning-bolt</v-icon>
                    测试连接
                  </v-btn>
                </v-card-text>
              </v-card>

              <v-alert
                v-if="testResult"
                :type="testResult.success ? 'success' : 'error'"
                class="mb-4"
              >
                <div class="font-weight-bold">{{ testResult.success ? '✓ 连接成功' : '✗ 连接失败' }}</div>
                <div class="text-caption">{{ testResult.message }}</div>
              </v-alert>
            </v-form>
          </v-card-text>

          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="grey"
              variant="text"
              @click="resetForm"
            >
              重置
            </v-btn>
            <v-btn
              color="primary"
              :disabled="!valid"
              :loading="saving"
              @click="saveConfig"
            >
              保存配置
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="3000"
    >
      {{ snackbar.message }}
      <template #actions>
        <v-btn
          color="white"
          variant="text"
          @click="snackbar.show = false"
        >
          关闭
        </v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'

interface ModelConfig {
  apiKey: string
  baseUrl: string
  model: string
  temperature: number
  maxTokens: number
}

interface TestResult {
  success: boolean
  message: string
}

interface SnackbarState {
  show: boolean
  message: string
  color: string
}

const valid = ref(false)
const showApiKey = ref(false)
const selectedModel = ref('')
const testing = ref(false)
const saving = ref(false)
const testMessage = ref('你好，请介绍一下你自己。')

const config = reactive<ModelConfig>({
  apiKey: '',
  baseUrl: '',
  model: '',
  temperature: 0.7,
  maxTokens: 2000
})

const testResult = ref<TestResult | null>(null)

const snackbar = reactive<SnackbarState>({
  show: false,
  message: '',
  color: 'success'
})

const modelOptions = [
  {
    name: '硅基流动 (SiliconFlow)',
    value: 'siliconflow',
    defaultConfig: {
      baseUrl: 'https://api.siliconflow.cn/v1/chat/completions',
      model: 'Qwen/Qwen2.5-72B-Instruct'
    }
  },
  {
    name: 'OpenAI GPT',
    value: 'openai',
    defaultConfig: {
      baseUrl: 'https://api.openai.com/v1/chat/completions',
      model: 'gpt-3.5-turbo'
    }
  },
  {
    name: '自定义',
    value: 'custom',
    defaultConfig: {
      baseUrl: '',
      model: ''
    }
  }
]

const apiKeyRules = [
  (v: string) => !!v || 'API Key 是必填项',
  (v: string) => v.length >= 10 || 'API Key 长度至少10位'
]

const urlRules = [
  (v: string) => !!v || 'API 地址是必填项',
  (v: string) => /^https?:\/\/.+/.test(v) || '请输入有效的URL地址'
]

const modelRules = [
  (v: string) => !!v || '模型名称是必填项'
]

const onModelChange = (value: string) => {
  const option = modelOptions.find(opt => opt.value === value)
  if (option && option.defaultConfig) {
    config.baseUrl = option.defaultConfig.baseUrl
    config.model = option.defaultConfig.model
  }
  testResult.value = null
}

const testConnection = async () => {
  if (!testMessage.value.trim()) {
    showSnackbar('请输入测试消息', 'warning')
    return
  }

  testing.value = true
  testResult.value = null

  try {
    const response = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/api/ai-config/test`, {
      config: config,
      message: testMessage.value
    })

    // 直接使用后端返回的结果
    testResult.value = {
      success: response.data.success,
      message: response.data.success 
        ? `响应时间: ${response.data.responseTime}ms` 
        : response.data.message
    }
  } catch (error: any) {
    testResult.value = {
      success: false,
      message: error.response?.data?.detail || error.message || '连接测试失败'
    }
  } finally {
    testing.value = false
  }
}

const saveConfig = async () => {
  saving.value = true

  try {
    await axios.post(`${import.meta.env.VITE_API_BASE_URL}/api/ai-config/save`, {
      provider: selectedModel.value,
      config: config
    })

    showSnackbar('配置保存成功', 'success')
  } catch (error: any) {
    showSnackbar('保存失败: ' + (error.response?.data?.detail || error.message), 'error')
  } finally {
    saving.value = false
  }
}

const loadConfig = async () => {
  try {
    const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/ai-config`)
    
    if (response.data) {
      selectedModel.value = response.data.provider || ''
      Object.assign(config, response.data.config || {})
    }
  } catch (error) {
    console.error('加载配置失败:', error)
  }
}

const resetForm = () => {
  selectedModel.value = ''
  Object.assign(config, {
    apiKey: '',
    baseUrl: '',
    model: '',
    temperature: 0.7,
    maxTokens: 2000
  })
  testResult.value = null
}

const showSnackbar = (message: string, color: string = 'success') => {
  snackbar.message = message
  snackbar.color = color
  snackbar.show = true
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.v-card {
  margin: 20px 0;
}
</style>