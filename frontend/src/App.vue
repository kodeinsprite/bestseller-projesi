<script setup>
import { computed, ref, watch, onMounted } from 'vue'

const API_BASE = import.meta.env.VITE_API_BASE || ''

const loadingBest = ref(false)
const loadingWorst = ref(false)
const errorBest = ref(null)
const errorWorst = ref(null)

const bestsellers = ref([])
const worstsellers = ref([])

const filterOptionsBest = ref({
  cinsiyet_options: [],
  anagrup_options: [],
  alt_kategori_options: [],
  renk_options: [],
  sezon_options: []
})

const filterOptionsWorst = ref({
  cinsiyet_options: [],
  anagrup_options: [],
  alt_kategori_options: [],
  renk_options: [],
  sezon_options: []
})

const metaBest = ref({ data_file: '' })
const metaWorst = ref({ data_file: '' })

// Bestseller filtreleri
const selectedCinsiyetBest = ref('')
const selectedAnagrupBest = ref('')
const selectedAltKategoriBest = ref('')
const selectedRenkBest = ref('')
const selectedSezonBest = ref('')

// Worstseller filtreleri
const selectedCinsiyetWorst = ref('')
const selectedAnagrupWorst = ref('')
const selectedAltKategoriWorst = ref('')
const selectedRenkWorst = ref('')
const selectedSezonWorst = ref('')

// Analytics
const loadingAnalytics = ref(false)
const errorAnalytics = ref(null)
const analyticsData = ref(null)
const analyticsSezon = ref('')
const analyticsAnagrup = ref('')
const analyticsCinsiyet = ref('')
const analyticsMetric = ref('satis') // satis | ciro | kar | st_pct

const navActive = ref('top10')
const showHelp = ref(false)
const isDarkMode = ref(true)

onMounted(() => {
  const savedMode = localStorage.getItem('theme')
  if (savedMode) {
    isDarkMode.value = savedMode === 'dark'
  }
})

function toggleTheme() {
  isDarkMode.value = !isDarkMode.value
  localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light')
}

// Bestseller Veri Çekme
async function fetchBest() {
  loadingBest.value = true
  errorBest.value = null
  try {
    const p = new URLSearchParams()
    if (selectedCinsiyetBest.value) p.set('cinsiyet', selectedCinsiyetBest.value)
    if (selectedAnagrupBest.value) p.set('anagrup', selectedAnagrupBest.value)
    if (selectedAltKategoriBest.value) p.set('alt_kategori', selectedAltKategoriBest.value)
    if (selectedRenkBest.value) p.set('renk', selectedRenkBest.value)
    if (selectedSezonBest.value) p.set('sezon', selectedSezonBest.value)
    
    const res = await fetch(`${API_BASE}/api/dashboard/bestseller?${p.toString()}`)
    if (!res.ok) throw new Error('Bestseller verisi alınamadı')
    const data = await res.json()
    bestsellers.value = data.bestsellers ?? []
    filterOptionsBest.value = data.filters ?? filterOptionsBest.value
    metaBest.value = data.meta ?? metaBest.value
  } catch (e) {
    errorBest.value = e.message
  } finally {
    loadingBest.value = false
  }
}

// Worstseller Veri Çekme
async function fetchWorst() {
  loadingWorst.value = true
  errorWorst.value = null
  try {
    const p = new URLSearchParams()
    if (selectedCinsiyetWorst.value) p.set('cinsiyet', selectedCinsiyetWorst.value)
    if (selectedAnagrupWorst.value) p.set('anagrup', selectedAnagrupWorst.value)
    if (selectedAltKategoriWorst.value) p.set('alt_kategori', selectedAltKategoriWorst.value)
    if (selectedRenkWorst.value) p.set('renk', selectedRenkWorst.value)
    if (selectedSezonWorst.value) p.set('sezon', selectedSezonWorst.value)
    
    const res = await fetch(`${API_BASE}/api/dashboard/worstseller?${p.toString()}`)
    if (!res.ok) throw new Error('Worstseller verisi alınamadı')
    const data = await res.json()
    worstsellers.value = data.worstsellers ?? []
    filterOptionsWorst.value = data.filters ?? filterOptionsWorst.value
    metaWorst.value = data.meta ?? metaWorst.value
  } catch (e) {
    errorWorst.value = e.message
  } finally {
    loadingWorst.value = false
  }
}

// Watchers for Bestseller filters
watch([selectedCinsiyetBest, selectedAnagrupBest, selectedAltKategoriBest, selectedRenkBest, selectedSezonBest], fetchBest, { immediate: true })

// Watchers for Worstseller filters
watch([selectedCinsiyetWorst, selectedAnagrupWorst, selectedAltKategoriWorst, selectedRenkWorst, selectedSezonWorst], fetchWorst, { immediate: true })

// Analytics
async function fetchAnalytics() {
  loadingAnalytics.value = true
  errorAnalytics.value = null
  try {
    const p = new URLSearchParams()
    if (analyticsSezon.value) p.set('sezon', analyticsSezon.value)
    if (analyticsAnagrup.value) p.set('anagrup', analyticsAnagrup.value)
    if (analyticsCinsiyet.value) p.set('cinsiyet', analyticsCinsiyet.value)
    const res = await fetch(`${API_BASE}/api/analytics/summary?${p.toString()}`)
    if (!res.ok) throw new Error('Analitik verisi alınamadı')
    analyticsData.value = await res.json()
  } catch (e) {
    errorAnalytics.value = e.message
  } finally {
    loadingAnalytics.value = false
  }
}

watch([analyticsSezon, analyticsAnagrup, analyticsCinsiyet], fetchAnalytics)
watch(navActive, (v) => { if (v === 'analytics' && !analyticsData.value) fetchAnalytics() })

const analyticsFilterOpts = computed(() => analyticsData.value?.filter_options ?? { sezon_options: [], anagrup_options: [], cinsiyet_options: [] })

const metricLabel = computed(() => ({ satis: 'Satış Adedi', ciro: 'Ciro (₺)', kar: 'Kar (₺)', st_pct: 'ST %' }[analyticsMetric.value]))

function mVal(row) {
  const m = analyticsMetric.value
  if (m === 'satis') return row.satis ?? 0
  if (m === 'ciro') return row.ciro ?? 0
  if (m === 'kar') return row.kar ?? 0
  if (m === 'st_pct') return row.st_pct ?? 0
  return 0
}

function mFmt(row) {
  const v = mVal(row)
  if (analyticsMetric.value === 'st_pct') return `%${Number(v).toLocaleString('tr-TR', { maximumFractionDigits: 1 })}`
  if (analyticsMetric.value === 'satis') return Number(v).toLocaleString('tr-TR')
  return Number(v).toLocaleString('tr-TR', { maximumFractionDigits: 0 }) + ' ₺'
}

function sortedByMetric(rows) {
  if (!rows || !rows.length) return []
  return [...rows].sort((a, b) => mVal(b) - mVal(a))
}

function maxOf(rows) {
  if (!rows || !rows.length) return 1
  return Math.max(...rows.map(mVal)) || 1
}

function barW(val, rows) {
  const max = maxOf(rows)
  if (!max) return 2
  return Math.max(2, Math.round((val / max) * 100))
}

const sortedBrands = computed(() => sortedByMetric(analyticsData.value?.by_brand ?? []))
const sortedKategori = computed(() => sortedByMetric(analyticsData.value?.by_kategori ?? []))
const sortedSezon = computed(() => sortedByMetric(analyticsData.value?.by_sezon ?? []))
const sortedCinsiyet = computed(() => sortedByMetric(analyticsData.value?.by_cinsiyet ?? []))

function onStarImgError(e) {
  e.target.src = PLACEHOLDER_IMG
}

function imgUrl(path) {
  if (!path) return PLACEHOLDER_IMG
  if (path.startsWith('http')) return path
  return API_BASE + path
}

function formatNum(v, suffix = '') {
  if (v === null || v === undefined || Number.isNaN(Number(v))) return '—'
  return `${Number(v).toLocaleString('tr-TR')}${suffix}`
}

function formatMoney(v) {
  return formatNum(v, ' ₺')
}

function formatPct(v) {
  if (v === null || v === undefined || Number.isNaN(Number(v))) return '—'
  return `%${Number(v).toLocaleString('tr-TR', { maximumFractionDigits: 1 })}`
}

function formatMu(v) {
  if (v === null || v === undefined || Number.isNaN(Number(v))) return '—'
  return `${Number(v).toLocaleString('tr-TR', { maximumFractionDigits: 4, minimumFractionDigits: 4 })}x`
}

function formatGmroi(v) {
  if (v === null || v === undefined || Number.isNaN(Number(v))) return '—'
  return `${Number(v).toLocaleString('tr-TR', { maximumFractionDigits: 2, minimumFractionDigits: 2 })}x`
}

const PLACEHOLDER_IMG = 'https://placehold.co/300x300/0b0f19/334155?text=No+Image'

function onImgError(e) {
  e.target.src = PLACEHOLDER_IMG
}

</script>

<template>
  <div class="flex h-screen transition-colors duration-500" :class="isDarkMode ? 'bg-[#0b0f19] text-slate-200' : 'bg-slate-50 text-slate-800'">
    <!-- Sidebar -->
    <aside class="hidden w-64 shrink-0 flex-col border-r py-6 px-5 lg:flex transition-colors duration-500" :class="isDarkMode ? 'border-white/10 bg-[#070a12]' : 'border-slate-200 bg-white shadow-sm'">
      <div class="mb-6">
        <!-- Sporthink Logo -->
        <img src="/sporthink-logo.png" alt="Sporthink" class="h-20 w-auto object-contain transition-all duration-300 -ml-1"
          :style="isDarkMode ? 'filter: brightness(0) invert(1)' : ''" />
        <p class="text-[10px] font-bold uppercase tracking-[0.2em] leading-none -mt-0.5" :class="isDarkMode ? 'text-slate-500' : 'text-slate-400'">B&amp;W Seller</p>
        <p class="text-lg font-bold tracking-tight leading-snug" :class="isDarkMode ? 'text-white' : 'text-slate-900'">Dashboard</p>
      </div>
      <nav class="flex flex-col gap-2 text-sm">
        <button 
          @click="navActive = 'top10'"
          class="flex items-center gap-3 rounded-xl px-4 py-3 font-medium transition duration-200"
          :class="navActive === 'top10' 
            ? (isDarkMode ? 'bg-sky-600/20 text-sky-400 ring-1 ring-sky-500/30' : 'bg-sky-50 text-sky-600 ring-1 ring-sky-200') 
            : (isDarkMode ? 'text-slate-400 hover:bg-white/5 hover:text-white' : 'text-slate-500 hover:bg-slate-100 hover:text-slate-900')"
        >
          <span class="text-lg">📊</span> Performans Raporu
        </button>
        <button 
          @click="navActive = 'analytics'"
          class="flex items-center gap-3 rounded-xl px-4 py-3 font-medium transition duration-200"
          :class="navActive === 'analytics' 
            ? (isDarkMode ? 'bg-violet-600/20 text-violet-400 ring-1 ring-violet-500/30' : 'bg-violet-50 text-violet-600 ring-1 ring-violet-200') 
            : (isDarkMode ? 'text-slate-400 hover:bg-white/5 hover:text-white' : 'text-slate-500 hover:bg-slate-100 hover:text-slate-900')"
        >
          <span class="text-lg">🔬</span> Marka Analizi
        </button>
        <button 
          @click="showHelp = true"
          class="flex items-center gap-3 rounded-xl px-4 py-3 font-medium transition duration-200"
          :class="isDarkMode ? 'text-slate-400 hover:bg-white/5 hover:text-white' : 'text-slate-500 hover:bg-slate-100 hover:text-slate-900'"
        >
          <span class="text-lg">💡</span> Terimler Sözlüğü
        </button>
      </nav>

      <div class="mt-auto space-y-6">
        <!-- Theme Toggle -->
        <div class="rounded-2xl p-4 transition-colors" :class="isDarkMode ? 'bg-white/5' : 'bg-slate-100'">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-500">Görünüm</span>
            <button @click="toggleTheme" class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 focus:outline-none ring-2 ring-transparent ring-offset-2" :class="isDarkMode ? 'bg-sky-600 ring-offset-[#070a12]' : 'bg-slate-300 ring-offset-white'">
              <span class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out" :class="isDarkMode ? 'translate-x-5' : 'translate-x-0'">
                <span class="absolute inset-0 flex h-full w-full items-center justify-center transition-opacity" :class="isDarkMode ? 'opacity-100' : 'opacity-0'">🌙</span>
                <span class="absolute inset-0 flex h-full w-full items-center justify-center transition-opacity" :class="isDarkMode ? 'opacity-0' : 'opacity-100'">☀️</span>
              </span>
            </button>
          </div>
        </div>

        <div class="pt-8 text-[11px] font-medium border-t" :class="isDarkMode ? 'text-slate-600 border-white/5' : 'text-slate-400 border-slate-100'">
          <p>Veri Kaynağı:</p>
          <p class="mt-1 font-mono break-all" :class="isDarkMode ? 'text-slate-500' : 'text-slate-500'">{{ metaBest.data_file || 'raw_data.xlsx' }}</p>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <div class="flex flex-1 flex-col overflow-hidden">
      <header class="border-b px-6 py-6 backdrop-blur-xl z-10 shrink-0 transition-colors duration-500" :class="isDarkMode ? 'border-white/10 bg-[#0b0f19]/80' : 'border-slate-200 bg-white/80'">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold tracking-tight" :class="isDarkMode ? 'text-white' : 'text-slate-900'">Perakende Performans Analizi</h1>
            <p class="mt-1 text-sm font-medium" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">Bestseller ve Worstseller verilerini profesyonel metriklerle analiz edin.</p>
          </div>
          <div class="flex items-center gap-4">
             <button @click="toggleTheme" class="lg:hidden h-10 w-10 rounded-xl flex items-center justify-center transition-colors" :class="isDarkMode ? 'bg-white/5 text-sky-400' : 'bg-slate-100 text-sky-600'">
               {{ isDarkMode ? '🌙' : '☀️' }}
             </button>
             <button @click="showHelp = true" class="lg:hidden text-sky-400 text-sm font-bold uppercase tracking-wider">Terimler</button>
          </div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto px-6 py-8 scroll-smooth">
        <div class="mx-auto max-w-7xl space-y-12 pb-20">

          <!-- ══════════════════ ANALYTICS PAGE ══════════════════ -->
          <div v-show="navActive === 'analytics'" class="space-y-8">

            <!-- Page header + filters row — STICKY -->
            <div class="sticky top-0 z-20 flex flex-col gap-5 rounded-2xl border p-5 backdrop-blur-xl"
              :class="isDarkMode ? 'border-white/10 bg-[#0b0f19]/92' : 'border-slate-200/80 bg-white/92 shadow-md'">
              <div class="flex items-start justify-between gap-4 flex-wrap">
                <div>
                  <p class="text-[10px] font-bold uppercase tracking-[0.25em] mb-1" :class="isDarkMode ? 'text-violet-500/80' : 'text-violet-500'">Analitik Merkez</p>
                  <h2 class="text-xl font-bold tracking-tight" :class="isDarkMode ? 'text-white' : 'text-slate-900'">Marka &amp; Kategori Analizi</h2>
                </div>
                <!-- Metric pill group -->
                <div class="flex items-center gap-1 rounded-xl p-1" :class="isDarkMode ? 'bg-white/5' : 'bg-slate-100'">
                  <button v-for="m in [{k:'satis',l:'Satış',ic:'📦'},{k:'ciro',l:'Ciro',ic:'💰'},{k:'kar',l:'Kar',ic:'📈'},{k:'st_pct',l:'Satış Oranı',ic:'🎯'}]" :key="m.k"
                    @click="analyticsMetric = m.k"
                    class="flex items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-bold transition-all duration-200"
                    :class="analyticsMetric === m.k
                      ? 'bg-violet-600 text-white shadow-lg shadow-violet-600/30'
                      : (isDarkMode ? 'text-slate-400 hover:text-white hover:bg-white/5' : 'text-slate-500 hover:text-slate-900 hover:bg-white')">
                    <span>{{ m.ic }}</span> {{ m.l }}
                  </button>
                </div>
              </div>
              <!-- Filters -->
              <div class="flex flex-wrap gap-3">
                <div class="space-y-1">
                  <label class="text-[10px] font-bold uppercase tracking-wider" :class="isDarkMode ? 'text-slate-500' : 'text-slate-400'">Sezon</label>
                  <select v-model="analyticsSezon" class="rounded-lg border px-3 py-2 text-xs outline-none transition focus:ring-2 min-w-[120px]" :class="isDarkMode ? 'border-white/10 bg-[#0f141f] text-slate-200 focus:ring-violet-500/40' : 'border-slate-200 bg-slate-50 text-slate-800'">
                    <option value="">Tüm Sezonlar</option>
                    <option v-for="o in analyticsFilterOpts.sezon_options" :key="o" :value="o">{{ o }}</option>
                  </select>
                </div>
                <div class="space-y-1">
                  <label class="text-[10px] font-bold uppercase tracking-wider" :class="isDarkMode ? 'text-slate-500' : 'text-slate-400'">Ana Kategori</label>
                  <select v-model="analyticsAnagrup" class="rounded-lg border px-3 py-2 text-xs outline-none transition focus:ring-2 min-w-[140px]" :class="isDarkMode ? 'border-white/10 bg-[#0f141f] text-slate-200 focus:ring-violet-500/40' : 'border-slate-200 bg-slate-50 text-slate-800'">
                    <option value="">Tüm Kategoriler</option>
                    <option v-for="o in analyticsFilterOpts.anagrup_options" :key="o" :value="o">{{ o }}</option>
                  </select>
                </div>
                <div class="space-y-1">
                  <label class="text-[10px] font-bold uppercase tracking-wider" :class="isDarkMode ? 'text-slate-500' : 'text-slate-400'">Cinsiyet</label>
                  <select v-model="analyticsCinsiyet" class="rounded-lg border px-3 py-2 text-xs outline-none transition focus:ring-2 min-w-[120px]" :class="isDarkMode ? 'border-white/10 bg-[#0f141f] text-slate-200 focus:ring-violet-500/40' : 'border-slate-200 bg-slate-50 text-slate-800'">
                    <option value="">Tümü</option>
                    <option v-for="o in analyticsFilterOpts.cinsiyet_options" :key="o" :value="o">{{ o }}</option>
                  </select>
                </div>
              </div>
            </div>

            <!-- Loading / Error -->
            <div v-if="loadingAnalytics" class="flex items-center justify-center py-24">
              <div class="flex flex-col items-center gap-3">
                <div class="h-10 w-10 animate-spin rounded-full border-4" :class="isDarkMode ? 'border-violet-500/20 border-t-violet-500' : 'border-violet-200 border-t-violet-600'"></div>
                <span class="text-xs font-bold uppercase tracking-widest" :class="isDarkMode ? 'text-violet-400' : 'text-violet-600'">Analiz Yükleniyor</span>
              </div>
            </div>
            <div v-else-if="errorAnalytics" class="py-6 px-4 rounded-xl border text-sm" :class="isDarkMode ? 'border-rose-500/30 bg-rose-950/20 text-rose-200' : 'border-rose-200 bg-rose-50 text-rose-700'">
              ⚠️ {{ errorAnalytics }}
            </div>

            <template v-else-if="analyticsData">

              <!-- KPI Cards -->
              <div class="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
                <div v-for="card in [
                  { label: 'Toplam Satış', value: formatNum(analyticsData.summary.total_satis), sub: 'adet', grad: 'from-sky-600/20 to-sky-900/10', border: isDarkMode ? 'border-sky-500/20' : 'border-sky-200', accent: isDarkMode ? 'text-sky-400' : 'text-sky-600', dot: 'bg-sky-500' },
                  { label: 'Toplam Ciro', value: formatMoney(analyticsData.summary.total_ciro), sub: '', grad: 'from-emerald-600/20 to-emerald-900/10', border: isDarkMode ? 'border-emerald-500/20' : 'border-emerald-200', accent: isDarkMode ? 'text-emerald-400' : 'text-emerald-600', dot: 'bg-emerald-500' },
                  { label: 'Toplam Kar', value: formatMoney(analyticsData.summary.total_kar), sub: '', grad: 'from-amber-600/20 to-amber-900/10', border: isDarkMode ? 'border-amber-500/20' : 'border-amber-200', accent: isDarkMode ? 'text-amber-400' : 'text-amber-600', dot: 'bg-amber-500' },
                  { label: 'Ort. Satış Oranı', value: formatPct(analyticsData.summary.avg_st_pct), sub: '', grad: 'from-violet-600/20 to-violet-900/10', border: isDarkMode ? 'border-violet-500/20' : 'border-violet-200', accent: isDarkMode ? 'text-violet-400' : 'text-violet-600', dot: 'bg-violet-500' },
                  { label: 'Dönem Sonu Stok', value: formatNum(analyticsData.summary.toplam_dss), sub: 'adet', grad: 'from-rose-600/20 to-rose-900/10', border: isDarkMode ? 'border-rose-500/20' : 'border-rose-200', accent: isDarkMode ? 'text-rose-400' : 'text-rose-600', dot: 'bg-rose-500' },
                  { label: 'Benzersiz Ürün', value: formatNum(analyticsData.summary.toplam_sku), sub: 'ürün', grad: 'from-slate-600/20 to-slate-900/10', border: isDarkMode ? 'border-white/10' : 'border-slate-200', accent: isDarkMode ? 'text-slate-300' : 'text-slate-600', dot: 'bg-slate-400' },
                ]" :key="card.label"
                  class="relative overflow-hidden rounded-2xl border p-4 bg-gradient-to-br transition-all duration-300 hover:scale-[1.02]"
                  :class="[card.border, card.grad]">
                  <div class="absolute top-3 right-3 h-1.5 w-1.5 rounded-full" :class="card.dot"></div>
                  <p class="text-[10px] font-bold uppercase tracking-wider mb-2.5" :class="isDarkMode ? 'text-slate-500' : 'text-slate-400'">{{ card.label }}</p>
                  <p class="text-base font-bold leading-none break-all" :class="card.accent">{{ card.value }}</p>
                  <p v-if="card.sub" class="text-[10px] mt-1.5 font-medium" :class="isDarkMode ? 'text-slate-600' : 'text-slate-400'">{{ card.sub }}</p>
                </div>
              </div>

              <!-- ⭐ Yıldız Ürünler -->
              <div class="rounded-2xl border p-5 space-y-4" :class="isDarkMode ? 'border-amber-500/20 bg-gradient-to-br from-amber-900/10 to-transparent' : 'border-amber-200 bg-amber-50/40'">
                <div class="flex items-center gap-2">
                  <span class="text-lg">⭐</span>
                  <div>
                    <h3 class="font-bold text-sm" :class="isDarkMode ? 'text-amber-300' : 'text-amber-700'">Yıldız Ürünler</h3>
                    <p class="text-[10px] uppercase tracking-wider font-semibold" :class="isDarkMode ? 'text-slate-500' : 'text-slate-400'">En Yüksek Sell-Through — Top 8</p>
                  </div>
                </div>
                <div class="flex gap-3 overflow-x-auto pb-2 snap-x">
                  <div v-for="(p, i) in analyticsData.top_products" :key="p.stok_kodu"
                    class="snap-start shrink-0 w-40 rounded-xl border p-3 space-y-2 transition hover:scale-[1.03] cursor-pointer"
                    :class="isDarkMode ? 'border-white/8 bg-[#0f141f]/80 hover:border-amber-500/40' : 'border-slate-200 bg-white hover:border-amber-400'">
                    <div class="relative">
                      <div class="h-28 w-full rounded-lg bg-white overflow-hidden flex items-center justify-center">
                        <img :src="imgUrl(p.gorsel_link)" @error="onStarImgError" class="h-full w-full object-contain" :alt="p.stok_aciklama" />
                      </div>
                      <span class="absolute top-1.5 left-1.5 h-5 w-5 rounded-full flex items-center justify-center text-[9px] font-black shadow"
                        :class="i === 0 ? 'bg-amber-400 text-amber-900' : i === 1 ? 'bg-slate-300 text-slate-700' : i === 2 ? 'bg-amber-700 text-amber-100' : (isDarkMode ? 'bg-white/10 text-slate-400' : 'bg-slate-100 text-slate-500')">
                        {{ i + 1 }}
                      </span>
                    </div>
                    <div class="space-y-1">
                      <p class="text-[10px] font-mono font-bold leading-none" :class="isDarkMode ? 'text-sky-400' : 'text-sky-600'">{{ p.stok_kodu }}</p>
                      <p class="text-[10px] font-medium leading-tight line-clamp-2 min-h-[24px]" :class="isDarkMode ? 'text-slate-300' : 'text-slate-700'">{{ p.stok_aciklama || p.marka }}</p>
                      <!-- Metrics grid -->
                      <div class="grid grid-cols-2 gap-1 pt-1.5 border-t" :class="isDarkMode ? 'border-white/5' : 'border-slate-100'">
                        <div>
                          <p class="text-[8px] uppercase tracking-wider font-bold" :class="isDarkMode ? 'text-slate-600' : 'text-slate-400'">Satış</p>
                          <p class="text-[10px] font-bold tabular-nums" :class="isDarkMode ? 'text-slate-200' : 'text-slate-800'">{{ formatNum(p.satis) }}</p>
                        </div>
                        <div>
                          <p class="text-[8px] uppercase tracking-wider font-bold" :class="isDarkMode ? 'text-slate-600' : 'text-slate-400'">Sat. Oranı</p>
                          <p class="text-[10px] font-bold tabular-nums" :class="isDarkMode ? 'text-emerald-400' : 'text-emerald-600'">%{{ p.st_pct }}</p>
                        </div>
                        <div>
                          <p class="text-[8px] uppercase tracking-wider font-bold" :class="isDarkMode ? 'text-slate-600' : 'text-slate-400'">GMROI</p>
                          <p class="text-[10px] font-bold tabular-nums" :class="isDarkMode ? 'text-violet-300' : 'text-violet-600'">{{ formatGmroi(p.gmroi) }}</p>
                        </div>
                        <div>
                          <p class="text-[8px] uppercase tracking-wider font-bold" :class="isDarkMode ? 'text-slate-600' : 'text-slate-400'">Kar</p>
                          <p class="text-[10px] font-bold tabular-nums truncate" :class="isDarkMode ? 'text-amber-300' : 'text-amber-600'">{{ formatMoney(p.kar) }}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- ⚠️ Risk Ürünleri (Worstseller) -->
              <div v-if="analyticsData.worst_products && analyticsData.worst_products.length" class="rounded-2xl border p-5 space-y-4" :class="isDarkMode ? 'border-rose-500/20 bg-gradient-to-br from-rose-900/10 to-transparent' : 'border-rose-200 bg-rose-50/40'">
                <div class="flex items-center gap-2">
                  <span class="text-lg">⚠️</span>
                  <div>
                    <h3 class="font-bold text-sm" :class="isDarkMode ? 'text-rose-300' : 'text-rose-700'">Risk Ürünleri</h3>
                    <p class="text-[10px] uppercase tracking-wider font-semibold" :class="isDarkMode ? 'text-slate-500' : 'text-slate-400'">En Düşük Sell-Through — Yüksek Stok Riski</p>
                  </div>
                </div>
                <div class="flex gap-3 overflow-x-auto pb-2 snap-x">
                  <div v-for="(p, i) in analyticsData.worst_products" :key="p.stok_kodu"
                    class="snap-start shrink-0 w-40 rounded-xl border p-3 space-y-2 transition hover:scale-[1.03] cursor-pointer"
                    :class="isDarkMode ? 'border-white/8 bg-[#0f141f]/80 hover:border-rose-500/40' : 'border-slate-200 bg-white hover:border-rose-400'">
                    <div class="relative">
                      <div class="h-28 w-full rounded-lg bg-white overflow-hidden flex items-center justify-center">
                        <img :src="imgUrl(p.gorsel_link)" @error="onStarImgError" class="h-full w-full object-contain" :alt="p.stok_aciklama" />
                      </div>
                      <span class="absolute top-1.5 left-1.5 h-5 w-5 rounded-full flex items-center justify-center text-[9px] font-black shadow"
                        :class="isDarkMode ? 'bg-rose-500/80 text-white' : 'bg-rose-500 text-white'">
                        {{ i + 1 }}
                      </span>
                    </div>
                    <div class="space-y-1">
                      <p class="text-[10px] font-mono font-bold leading-none" :class="isDarkMode ? 'text-sky-400' : 'text-sky-600'">{{ p.stok_kodu }}</p>
                      <p class="text-[10px] font-medium leading-tight line-clamp-2 min-h-[24px]" :class="isDarkMode ? 'text-slate-300' : 'text-slate-700'">{{ p.stok_aciklama || p.marka }}</p>
                      <div class="grid grid-cols-2 gap-1 pt-1.5 border-t" :class="isDarkMode ? 'border-white/5' : 'border-slate-100'">
                        <div>
                          <p class="text-[8px] uppercase tracking-wider font-bold" :class="isDarkMode ? 'text-slate-600' : 'text-slate-400'">Satış</p>
                          <p class="text-[10px] font-bold tabular-nums" :class="isDarkMode ? 'text-slate-200' : 'text-slate-800'">{{ formatNum(p.satis) }}</p>
                        </div>
                        <div>
                          <p class="text-[8px] uppercase tracking-wider font-bold" :class="isDarkMode ? 'text-slate-600' : 'text-slate-400'">Stok</p>
                          <p class="text-[10px] font-bold tabular-nums" :class="isDarkMode ? 'text-rose-300' : 'text-rose-600'">{{ formatNum(p.dss) }}</p>
                        </div>
                        <div>
                          <p class="text-[8px] uppercase tracking-wider font-bold" :class="isDarkMode ? 'text-slate-600' : 'text-slate-400'">Sat. Oranı</p>
                          <p class="text-[10px] font-bold tabular-nums" :class="isDarkMode ? 'text-rose-300' : 'text-rose-600'">%{{ p.st_pct }}</p>
                        </div>
                        <div>
                          <p class="text-[8px] uppercase tracking-wider font-bold" :class="isDarkMode ? 'text-slate-600' : 'text-slate-400'">GMROI</p>
                          <p class="text-[10px] font-bold tabular-nums" :class="isDarkMode ? 'text-violet-300' : 'text-violet-600'">{{ formatGmroi(p.gmroi) }}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Brand + Category Charts -->
              <div class="grid grid-cols-1 gap-5 lg:grid-cols-2">

                <!-- Marka Analizi -->
                <div class="rounded-2xl border p-5 space-y-4" :class="isDarkMode ? 'border-white/8 bg-[#0e1320]' : 'border-slate-200 bg-white'">
                  <div class="flex items-baseline justify-between">
                    <div>
                      <h3 class="font-bold text-sm" :class="isDarkMode ? 'text-white' : 'text-slate-900'">Marka Sıralaması</h3>
                      <p class="text-[10px] mt-0.5 uppercase tracking-wider" :class="isDarkMode ? 'text-slate-500' : 'text-slate-400'">{{ metricLabel }} · Top 15</p>
                    </div>
                    <span class="text-[10px] font-bold rounded-full px-2 py-0.5" :class="isDarkMode ? 'bg-violet-500/15 text-violet-400' : 'bg-violet-50 text-violet-600'">{{ sortedBrands.length }} marka</span>
                  </div>
                  <div class="space-y-2.5">
                    <div v-for="(row, idx) in sortedBrands" :key="row.label">
                      <div class="flex items-center justify-between mb-1">
                        <div class="flex items-center gap-2 min-w-0">
                          <span class="text-[9px] font-black w-4 text-right shrink-0" :class="idx < 3 ? (isDarkMode ? 'text-violet-400' : 'text-violet-500') : (isDarkMode ? 'text-slate-600' : 'text-slate-400')">{{ idx + 1 }}</span>
                          <span class="text-xs font-semibold truncate" :class="isDarkMode ? 'text-slate-200' : 'text-slate-700'">{{ row.label }}</span>
                        </div>
                        <div class="flex items-center gap-2 shrink-0 ml-2">
                          <span class="text-[9px]" :class="isDarkMode ? 'text-slate-600' : 'text-slate-400'">{{ row.sku_count }} ürün</span>
                          <span class="text-[11px] font-bold tabular-nums min-w-[70px] text-right" :class="isDarkMode ? 'text-violet-300' : 'text-violet-700'">{{ mFmt(row) }}</span>
                        </div>
                      </div>
                      <div class="h-1.5 w-full rounded-full" :class="isDarkMode ? 'bg-white/5' : 'bg-slate-100'">
                        <div class="h-full rounded-full transition-all duration-700 ease-out"
                          :style="{ width: barW(mVal(row), sortedBrands) + '%' }"
                          :class="idx === 0 ? 'bg-gradient-to-r from-violet-500 to-violet-300' : idx < 3 ? 'bg-gradient-to-r from-violet-600/80 to-violet-400/80' : (isDarkMode ? 'bg-violet-700/50' : 'bg-violet-300/70')">
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Kategori Analizi -->
                <div class="rounded-2xl border p-5 space-y-4" :class="isDarkMode ? 'border-white/8 bg-[#0e1320]' : 'border-slate-200 bg-white'">
                  <div class="flex items-baseline justify-between">
                    <div>
                      <h3 class="font-bold text-sm" :class="isDarkMode ? 'text-white' : 'text-slate-900'">Ürün Grubu Sıralaması</h3>
                      <p class="text-[10px] mt-0.5 uppercase tracking-wider" :class="isDarkMode ? 'text-slate-500' : 'text-slate-400'">{{ metricLabel }} · Alt Kategoriler</p>
                    </div>
                    <span class="text-[10px] font-bold rounded-full px-2 py-0.5" :class="isDarkMode ? 'bg-sky-500/15 text-sky-400' : 'bg-sky-50 text-sky-600'">{{ sortedKategori.length }} grup</span>
                  </div>
                  <div class="space-y-2.5">
                    <div v-for="(row, idx) in sortedKategori" :key="row.label">
                      <div class="flex items-center justify-between mb-1">
                        <div class="flex items-center gap-2 min-w-0">
                          <span class="text-[9px] font-black w-4 text-right shrink-0" :class="idx < 3 ? (isDarkMode ? 'text-sky-400' : 'text-sky-500') : (isDarkMode ? 'text-slate-600' : 'text-slate-400')">{{ idx + 1 }}</span>
                          <span class="text-xs font-semibold truncate" :class="isDarkMode ? 'text-slate-200' : 'text-slate-700'">{{ row.label }}</span>
                        </div>
                        <div class="flex items-center gap-2 shrink-0 ml-2">
                          <span class="text-[9px]" :class="isDarkMode ? 'text-slate-600' : 'text-slate-400'">{{ row.sku_count }} ürün</span>
                          <span class="text-[11px] font-bold tabular-nums min-w-[70px] text-right" :class="isDarkMode ? 'text-sky-300' : 'text-sky-700'">{{ mFmt(row) }}</span>
                        </div>
                      </div>
                      <div class="h-1.5 w-full rounded-full" :class="isDarkMode ? 'bg-white/5' : 'bg-slate-100'">
                        <div class="h-full rounded-full transition-all duration-700 ease-out"
                          :style="{ width: barW(mVal(row), sortedKategori) + '%' }"
                          :class="idx === 0 ? 'bg-gradient-to-r from-sky-500 to-sky-300' : idx < 3 ? 'bg-gradient-to-r from-sky-600/80 to-sky-400/80' : (isDarkMode ? 'bg-sky-700/50' : 'bg-sky-300/70')">
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- ST% Distribution + Season + Gender -->
              <div class="grid grid-cols-1 gap-5 lg:grid-cols-3">

                <!-- ST% Histogram -->
                <div class="rounded-2xl border p-5 space-y-4" :class="isDarkMode ? 'border-white/8 bg-[#0e1320]' : 'border-slate-200 bg-white'">
                  <div>
                    <h3 class="font-bold text-sm" :class="isDarkMode ? 'text-white' : 'text-slate-900'">Sell-Through Dağılımı</h3>
                    <p class="text-[10px] mt-0.5 uppercase tracking-wider" :class="isDarkMode ? 'text-slate-500' : 'text-slate-400'">Ürün sayısına göre satış oranı dağılımı</p>
                  </div>
                  <div class="relative h-40 flex items-end gap-2">
                    <div v-for="b in analyticsData.st_distribution" :key="b.label" class="flex-1 flex flex-col items-center gap-1.5 h-full justify-end">
                      <span class="text-[10px] font-bold tabular-nums" :class="isDarkMode ? 'text-slate-400' : 'text-slate-600'">{{ b.count }}</span>
                      <div class="w-full rounded-t-lg transition-all duration-700 ease-out min-h-[4px]"
                        :style="{ height: Math.max(4, Math.round((b.count / Math.max(...analyticsData.st_distribution.map(x=>x.count))) * 110)) + 'px' }"
                        :class="b.label.includes('Satışsız')
                          ? (isDarkMode ? 'bg-gradient-to-t from-rose-700 to-rose-500' : 'bg-gradient-to-t from-rose-600 to-rose-400')
                          : (isDarkMode ? 'bg-gradient-to-t from-emerald-700 to-emerald-500' : 'bg-gradient-to-t from-emerald-600 to-emerald-400')">
                      </div>
                      <span class="text-[9px] font-medium text-center leading-tight" :class="isDarkMode ? 'text-slate-500' : 'text-slate-500'">{{ b.label }}</span>
                    </div>
                  </div>
                </div>

                <!-- Sezon -->
                <div class="rounded-2xl border p-5 space-y-4" :class="isDarkMode ? 'border-white/8 bg-[#0e1320]' : 'border-slate-200 bg-white'">
                  <div>
                    <h3 class="font-bold text-sm" :class="isDarkMode ? 'text-white' : 'text-slate-900'">Sezon Karşılaştırması</h3>
                    <p class="text-[10px] mt-0.5 uppercase tracking-wider" :class="isDarkMode ? 'text-slate-500' : 'text-slate-400'">{{ metricLabel }}</p>
                  </div>
                  <div class="space-y-3">
                    <div v-for="(row, idx) in sortedSezon" :key="row.label">
                      <div class="flex items-center justify-between mb-1">
                        <span class="text-xs font-semibold" :class="isDarkMode ? 'text-slate-200' : 'text-slate-700'">{{ row.label }}</span>
                        <span class="text-xs font-bold tabular-nums" :class="isDarkMode ? 'text-amber-300' : 'text-amber-700'">{{ mFmt(row) }}</span>
                      </div>
                      <div class="h-2 w-full rounded-full" :class="isDarkMode ? 'bg-white/5' : 'bg-slate-100'">
                        <div class="h-full rounded-full transition-all duration-700 ease-out"
                          :style="{ width: barW(mVal(row), sortedSezon) + '%' }"
                          :class="idx === 0 ? 'bg-gradient-to-r from-amber-500 to-amber-300' : (isDarkMode ? 'bg-amber-700/60' : 'bg-amber-300/70')">
                        </div>
                      </div>
                    </div>
                    <p v-if="!sortedSezon.length" class="text-xs italic" :class="isDarkMode ? 'text-slate-600' : 'text-slate-400'">Sezon verisi bulunamadı.</p>
                  </div>
                </div>

                <!-- Cinsiyet -->
                <div class="rounded-2xl border p-5 space-y-4" :class="isDarkMode ? 'border-white/8 bg-[#0e1320]' : 'border-slate-200 bg-white'">
                  <div>
                    <h3 class="font-bold text-sm" :class="isDarkMode ? 'text-white' : 'text-slate-900'">Cinsiyet Dağılımı</h3>
                    <p class="text-[10px] mt-0.5 uppercase tracking-wider" :class="isDarkMode ? 'text-slate-500' : 'text-slate-400'">{{ metricLabel }}</p>
                  </div>
                  <div class="space-y-3">
                    <div v-for="(row, idx) in sortedCinsiyet" :key="row.label">
                      <div class="flex items-center justify-between mb-1">
                        <span class="text-xs font-semibold" :class="isDarkMode ? 'text-slate-200' : 'text-slate-700'">{{ row.label }}</span>
                        <span class="text-xs font-bold tabular-nums" :class="isDarkMode ? 'text-pink-300' : 'text-pink-700'">{{ mFmt(row) }}</span>
                      </div>
                      <div class="h-2 w-full rounded-full" :class="isDarkMode ? 'bg-white/5' : 'bg-slate-100'">
                        <div class="h-full rounded-full transition-all duration-700 ease-out"
                          :style="{ width: barW(mVal(row), sortedCinsiyet) + '%' }"
                          :class="idx === 0 ? 'bg-gradient-to-r from-pink-500 to-pink-300' : (isDarkMode ? 'bg-pink-700/60' : 'bg-pink-300/70')">
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Ana Kategori tablo -->
              <div class="rounded-2xl border overflow-hidden" :class="isDarkMode ? 'border-white/8' : 'border-slate-200'">
                <div class="px-5 py-4 border-b" :class="isDarkMode ? 'border-white/5 bg-[#0e1320]' : 'border-slate-100 bg-slate-50'">
                  <h3 class="font-bold text-sm" :class="isDarkMode ? 'text-white' : 'text-slate-900'">Ana Kategori Özeti</h3>
                  <p class="text-[10px] mt-0.5 uppercase tracking-wider" :class="isDarkMode ? 'text-slate-500' : 'text-slate-400'">Tüm metrikler karşılaştırmalı</p>
                </div>
                <div class="overflow-x-auto">
                  <table class="w-full text-xs border-collapse">
                    <thead>
                      <tr class="text-[10px] font-bold uppercase tracking-wider border-b" :class="isDarkMode ? 'bg-white/3 text-slate-500 border-white/5' : 'bg-slate-50 text-slate-400 border-slate-200'">
                        <th class="px-5 py-3 text-left">Ana Kategori</th>
                        <th class="px-4 py-3 text-right">Ürün Sayısı</th>
                        <th class="px-4 py-3 text-right">Satış Adedi</th>
                        <th class="px-4 py-3 text-right">Dönem Sonu Stok</th>
                        <th class="px-4 py-3 text-right" :class="isDarkMode ? 'text-violet-400' : 'text-violet-600'">Satış Oranı</th>
                        <th class="px-4 py-3 text-right">Ciro</th>
                        <th class="px-4 py-3 text-right" :class="isDarkMode ? 'text-emerald-400' : 'text-emerald-600'">Kar</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y" :class="isDarkMode ? 'divide-white/5' : 'divide-slate-100'">
                      <tr v-for="row in analyticsData.by_anagrup" :key="row.label"
                        class="transition-colors duration-150"
                        :class="isDarkMode ? 'hover:bg-white/3' : 'hover:bg-slate-50/80'">
                        <td class="px-5 py-3 font-semibold" :class="isDarkMode ? 'text-slate-200' : 'text-slate-800'">{{ row.label }}</td>
                        <td class="px-4 py-3 text-right tabular-nums" :class="isDarkMode ? 'text-slate-500' : 'text-slate-400'">{{ row.sku_count }}</td>
                        <td class="px-4 py-3 text-right tabular-nums font-bold" :class="isDarkMode ? 'text-slate-200' : 'text-slate-800'">{{ formatNum(row.satis) }}</td>
                        <td class="px-4 py-3 text-right tabular-nums" :class="isDarkMode ? 'text-rose-300' : 'text-rose-600'">{{ formatNum(row.dss) }}</td>
                        <td class="px-4 py-3 text-right tabular-nums font-bold" :class="isDarkMode ? 'text-violet-400' : 'text-violet-600'">{{ formatPct(row.st_pct) }}</td>
                        <td class="px-4 py-3 text-right tabular-nums" :class="isDarkMode ? 'text-slate-300' : 'text-slate-600'">{{ formatMoney(row.ciro) }}</td>
                        <td class="px-4 py-3 text-right tabular-nums font-bold" :class="isDarkMode ? 'text-emerald-400' : 'text-emerald-600'">{{ formatMoney(row.kar) }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

            </template>
          </div>
          <!-- ══════════════════ END ANALYTICS ══════════════════ -->

          <div v-show="navActive === 'top10'">
          <!-- BESTSELLER SECTION -->
          <section class="space-y-6">
            <div class="flex flex-col gap-6 rounded-2xl border p-6 shadow-xl transition-all duration-500" 
                 :class="isDarkMode ? 'border-emerald-500/20 bg-[#121722]/50 shadow-emerald-950/5' : 'border-emerald-200 bg-white shadow-emerald-100/20'">
              <div class="flex items-center justify-between border-b pb-4" :class="isDarkMode ? 'border-white/5' : 'border-slate-100'">
                <div>
                  <h2 class="text-lg font-bold flex items-center gap-2" :class="isDarkMode ? 'text-emerald-400' : 'text-emerald-600'">
                    <span class="text-xl">🏆</span> BESTSELLER LİSTESİ (İLK 10)
                  </h2>
                  <p class="text-xs mt-1 uppercase tracking-wider font-semibold" :class="isDarkMode ? 'text-slate-500' : 'text-slate-400'">Satış Hızı ve Karlılık Analizi</p>
                </div>
              </div>

              <!-- Bestseller Filtreleri -->
              <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
                <!-- Sezon -->
                <div class="space-y-1.5">
                  <label class="text-[11px] font-bold uppercase tracking-wider ml-1" :class="isDarkMode ? 'text-slate-500' : 'text-slate-400'">Sezon</label>
                  <select v-model="selectedSezonBest" class="w-full rounded-xl border px-4 py-2.5 text-sm outline-none transition focus:ring-2" :class="isDarkMode ? 'border-white/10 bg-[#0f141f] text-white ring-emerald-500/40 focus:border-emerald-500/50' : 'border-slate-200 bg-slate-50 text-slate-800 ring-emerald-500/20 focus:border-emerald-500/50'">
                    <option value="">Tümü</option>
                    <option v-for="opt in filterOptionsBest.sezon_options" :key="opt" :value="opt">{{ opt }}</option>
                  </select>
                </div>
                <!-- Cinsiyet -->
                <div class="space-y-1.5">
                  <label class="text-[11px] font-bold uppercase tracking-wider ml-1" :class="isDarkMode ? 'text-slate-500' : 'text-slate-400'">Cinsiyet</label>
                  <select v-model="selectedCinsiyetBest" class="w-full rounded-xl border px-4 py-2.5 text-sm outline-none transition focus:ring-2" :class="isDarkMode ? 'border-white/10 bg-[#0f141f] text-white ring-emerald-500/40 focus:border-emerald-500/50' : 'border-slate-200 bg-slate-50 text-slate-800 ring-emerald-500/20 focus:border-emerald-500/50'">
                    <option value="">Tümü</option>
                    <option v-for="opt in filterOptionsBest.cinsiyet_options" :key="opt" :value="opt">{{ opt }}</option>
                  </select>
                </div>
                <!-- Ana Kategori -->
                <div class="space-y-1.5">
                  <label class="text-[11px] font-bold uppercase tracking-wider ml-1" :class="isDarkMode ? 'text-slate-500' : 'text-slate-400'">Ana Kategori</label>
                  <select v-model="selectedAnagrupBest" class="w-full rounded-xl border px-4 py-2.5 text-sm outline-none transition focus:ring-2" :class="isDarkMode ? 'border-white/10 bg-[#0f141f] text-white ring-emerald-500/40 focus:border-emerald-500/50' : 'border-slate-200 bg-slate-50 text-slate-800 ring-emerald-500/20 focus:border-emerald-500/50'">
                    <option value="">Tümü</option>
                    <option v-for="opt in filterOptionsBest.anagrup_options" :key="opt" :value="opt">{{ opt }}</option>
                  </select>
                </div>
                <!-- Ürün Grubu -->
                <div class="space-y-1.5">
                  <label class="text-[11px] font-bold uppercase tracking-wider ml-1" :class="isDarkMode ? 'text-slate-500' : 'text-slate-400'">Ürün Grubu</label>
                  <select v-model="selectedAltKategoriBest" class="w-full rounded-xl border px-4 py-2.5 text-sm outline-none transition focus:ring-2" :class="isDarkMode ? 'border-white/10 bg-[#0f141f] text-white ring-emerald-500/40 focus:border-emerald-500/50' : 'border-slate-200 bg-slate-50 text-slate-800 ring-emerald-500/20 focus:border-emerald-500/50'">
                    <option value="">Tümü</option>
                    <option v-for="opt in filterOptionsBest.alt_kategori_options" :key="opt" :value="opt">{{ opt }}</option>
                  </select>
                </div>
                <!-- Renk -->
                <div class="space-y-1.5">
                  <label class="text-[11px] font-bold uppercase tracking-wider ml-1" :class="isDarkMode ? 'text-slate-500' : 'text-slate-400'">Renk</label>
                  <select v-model="selectedRenkBest" class="w-full rounded-xl border px-4 py-2.5 text-sm outline-none transition focus:ring-2" :class="isDarkMode ? 'border-white/10 bg-[#0f141f] text-white ring-emerald-500/40 focus:border-emerald-500/50' : 'border-slate-200 bg-slate-50 text-slate-800 ring-emerald-500/20 focus:border-emerald-500/50'">
                    <option value="">Tümü</option>
                    <option v-for="opt in filterOptionsBest.renk_options" :key="opt" :value="opt">{{ opt }}</option>
                  </select>
                </div>
              </div>

              <!-- Bestseller Tablo -->
              <div class="relative min-h-[400px]">
                <!-- Loading Overlay -->
                <div v-if="loadingBest" class="absolute inset-0 z-20 flex items-center justify-center rounded-xl backdrop-blur-[2px] transition-opacity duration-300" :class="isDarkMode ? 'bg-[#121722]/60' : 'bg-white/60'">
                  <div class="flex flex-col items-center gap-3">
                    <div class="h-10 w-10 animate-spin rounded-full border-4" :class="isDarkMode ? 'border-sky-500/20 border-t-sky-500' : 'border-sky-200 border-t-sky-600'"></div>
                    <span class="text-xs font-bold uppercase tracking-widest" :class="isDarkMode ? 'text-sky-400' : 'text-sky-600'">Veriler Güncelleniyor</span>
                  </div>
                </div>

                <div v-if="errorBest" class="py-8 px-4 rounded-xl border text-sm" :class="isDarkMode ? 'border-rose-500/30 bg-rose-950/20 text-rose-200' : 'border-rose-200 bg-rose-50 text-rose-700'">
                  <p class="font-bold">⚠️ Bestseller hatası:</p>
                  <p class="mt-1 opacity-80">{{ errorBest }}</p>
                </div>
                <div v-else-if="!loadingBest && !bestsellers.length" class="py-12 text-center text-sm italic" :class="isDarkMode ? 'text-slate-500' : 'text-slate-400'">Veri bulunamadı.</div>
                <div v-else class="overflow-hidden rounded-xl border transition-all duration-500" :class="[isDarkMode ? 'border-white/5 bg-[#0b0f19]' : 'border-slate-200 bg-white', {'opacity-40 pointer-events-none': loadingBest}]">
                  <div class="overflow-x-auto">
                    <table class="w-full min-w-[1000px] border-collapse text-left text-xs">
                      <thead>
                        <tr class="border-b text-[10px] font-bold uppercase tracking-wider" :class="isDarkMode ? 'border-white/10 bg-white/5 text-slate-400' : 'border-slate-100 bg-slate-50 text-slate-500'">
                          <th class="px-4 py-3.5">#</th>
                          <th class="px-4 py-3.5">Resim</th>
                          <th class="px-4 py-3.5">Stok Kodu</th>
                          <th class="px-4 py-3.5">Ürün Açıklama</th>
                          <th class="px-4 py-3.5 text-right">Satış</th>
                          <th class="px-4 py-3.5 text-right">Ciro</th>
                          <th class="px-4 py-3.5 text-right font-bold" :class="isDarkMode ? 'text-emerald-400' : 'text-emerald-600'">Satış Oranı</th>
                          <th class="px-4 py-3.5 text-right">Mark-Up</th>
                          <th class="px-4 py-3.5 text-right font-semibold" :class="isDarkMode ? 'text-violet-300' : 'text-violet-600'">GMROI</th>
                          <th class="px-4 py-3.5 text-right font-semibold" :class="isDarkMode ? 'text-emerald-300' : 'text-emerald-600'">Kar</th>
                        </tr>
                      </thead>
                      <tbody class="divide-y" :class="isDarkMode ? 'divide-white/5' : 'divide-slate-100'">
                        <tr v-for="(item, idx) in bestsellers" :key="item.stok_kodu" class="transition duration-150 group" :class="isDarkMode ? 'hover:bg-emerald-500/5' : 'hover:bg-emerald-50/50'">
                          <td class="px-4 py-3.5 font-medium" :class="isDarkMode ? 'text-slate-500' : 'text-slate-400'">{{ idx + 1 }}</td>
                          <td class="px-4 py-3.5">
                            <a :href="item.product_url || '#'" target="_blank" rel="noopener noreferrer" class="inline-block">
                              <div class="h-36 w-36 rounded-lg bg-white overflow-hidden ring-1 transition group-hover:scale-110" :class="isDarkMode ? 'ring-white/10' : 'ring-slate-200'">
                                <img :src="imgUrl(item.gorsel_link)" @error="onImgError" class="h-full w-full object-contain" alt="product" />
                              </div>
                            </a>
                          </td>
                          <td class="px-4 py-3.5 font-mono font-semibold uppercase" :class="isDarkMode ? 'text-sky-400' : 'text-sky-600'">{{ item.stok_kodu }}</td>
                          <td class="px-4 py-3.5 font-medium">
                            <div :class="isDarkMode ? 'text-slate-200' : 'text-slate-900'">{{ item.stok_aciklama }}</div>
                            <div class="text-[10px] mt-0.5 font-normal" :class="isDarkMode ? 'text-slate-500' : 'text-slate-500'">{{ item.marka_aciklama }} • {{ item.renk_aciklama }}</div>
                          </td>
                          <td class="px-4 py-3.5 text-right tabular-nums font-bold">{{ formatNum(item.satis_miktari) }}</td>
                          <td class="px-4 py-3.5 text-right tabular-nums" :class="isDarkMode ? 'text-slate-300' : 'text-slate-600'">{{ formatMoney(item.satis_tutari) }}</td>
                          <td class="px-4 py-3.5 text-right tabular-nums font-bold" :class="isDarkMode ? 'text-emerald-400 bg-emerald-500/5' : 'text-emerald-600 bg-emerald-50/50'">{{ formatPct(item.sell_through_pct) }}</td>
                          <td class="px-4 py-3.5 text-right tabular-nums" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">{{ formatMu(item.mu) }}</td>
                          <td class="px-4 py-3.5 text-right tabular-nums font-semibold" :class="isDarkMode ? 'text-violet-300' : 'text-violet-600'">{{ formatGmroi(item.gmroi) }}</td>
                          <td class="px-4 py-3.5 text-right tabular-nums font-semibold" :class="isDarkMode ? 'text-emerald-300' : 'text-emerald-600'">{{ formatMoney(item.toplam_kar) }}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <!-- WORSTSELLER SECTION -->
          <section class="space-y-6">
            <div class="flex flex-col gap-6 rounded-2xl border p-6 shadow-xl transition-all duration-500"
                 :class="isDarkMode ? 'border-rose-500/20 bg-[#121722]/50 shadow-rose-950/5' : 'border-rose-200 bg-white shadow-rose-100/20'">
              <div class="flex items-center justify-between border-b pb-4" :class="isDarkMode ? 'border-white/5' : 'border-slate-100'">
                <div>
                  <h2 class="text-lg font-bold flex items-center gap-2" :class="isDarkMode ? 'text-rose-400' : 'text-rose-600'">
                    <span class="text-xl">📉</span> WORSTSELLER LİSTESİ (İLK 10)
                  </h2>
                  <p class="text-xs mt-1 uppercase tracking-wider font-semibold" :class="isDarkMode ? 'text-slate-500' : 'text-slate-400'">Stok Riski ve Verimsizlik Analizi</p>
                </div>
              </div>

              <!-- Worstseller Filtreleri -->
              <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
                <!-- Sezon -->
                <div class="space-y-1.5">
                  <label class="text-[11px] font-bold uppercase tracking-wider ml-1" :class="isDarkMode ? 'text-slate-500' : 'text-slate-400'">Sezon</label>
                  <select v-model="selectedSezonWorst" class="w-full rounded-xl border px-4 py-2.5 text-sm outline-none transition focus:ring-2" :class="isDarkMode ? 'border-white/10 bg-[#0f141f] text-white ring-rose-500/40 focus:border-emerald-500/50' : 'border-slate-200 bg-slate-50 text-slate-800 ring-rose-500/20 focus:border-emerald-500/50'">
                    <option value="">Tümü</option>
                    <option v-for="opt in filterOptionsWorst.sezon_options" :key="opt" :value="opt">{{ opt }}</option>
                  </select>
                </div>
                <!-- Cinsiyet -->
                <div class="space-y-1.5">
                  <label class="text-[11px] font-bold uppercase tracking-wider ml-1" :class="isDarkMode ? 'text-slate-500' : 'text-slate-400'">Cinsiyet</label>
                  <select v-model="selectedCinsiyetWorst" class="w-full rounded-xl border px-4 py-2.5 text-sm outline-none transition focus:ring-2" :class="isDarkMode ? 'border-white/10 bg-[#0f141f] text-white ring-rose-500/40 focus:border-emerald-500/50' : 'border-slate-200 bg-slate-50 text-slate-800 ring-rose-500/20 focus:border-emerald-500/50'">
                    <option value="">Tümü</option>
                    <option v-for="opt in filterOptionsWorst.cinsiyet_options" :key="opt" :value="opt">{{ opt }}</option>
                  </select>
                </div>
                <!-- Ana Kategori -->
                <div class="space-y-1.5">
                  <label class="text-[11px] font-bold uppercase tracking-wider ml-1" :class="isDarkMode ? 'text-slate-500' : 'text-slate-400'">Ana Kategori</label>
                  <select v-model="selectedAnagrupWorst" class="w-full rounded-xl border px-4 py-2.5 text-sm outline-none transition focus:ring-2" :class="isDarkMode ? 'border-white/10 bg-[#0f141f] text-white ring-rose-500/40 focus:border-emerald-500/50' : 'border-slate-200 bg-slate-50 text-slate-800 ring-rose-500/20 focus:border-emerald-500/50'">
                    <option value="">Tümü</option>
                    <option v-for="opt in filterOptionsWorst.anagrup_options" :key="opt" :value="opt">{{ opt }}</option>
                  </select>
                </div>
                <!-- Ürün Grubu -->
                <div class="space-y-1.5">
                  <label class="text-[11px] font-bold uppercase tracking-wider ml-1" :class="isDarkMode ? 'text-slate-500' : 'text-slate-400'">Ürün Grubu</label>
                  <select v-model="selectedAltKategoriWorst" class="w-full rounded-xl border px-4 py-2.5 text-sm outline-none transition focus:ring-2" :class="isDarkMode ? 'border-white/10 bg-[#0f141f] text-white ring-rose-500/40 focus:border-emerald-500/50' : 'border-slate-200 bg-slate-50 text-slate-800 ring-rose-500/20 focus:border-emerald-500/50'">
                    <option value="">Tümü</option>
                    <option v-for="opt in filterOptionsWorst.alt_kategori_options" :key="opt" :value="opt">{{ opt }}</option>
                  </select>
                </div>
                <!-- Renk -->
                <div class="space-y-1.5">
                  <label class="text-[11px] font-bold uppercase tracking-wider ml-1" :class="isDarkMode ? 'text-slate-500' : 'text-slate-400'">Renk</label>
                  <select v-model="selectedRenkWorst" class="w-full rounded-xl border px-4 py-2.5 text-sm outline-none transition focus:ring-2" :class="isDarkMode ? 'border-white/10 bg-[#0f141f] text-white ring-rose-500/40 focus:border-emerald-500/50' : 'border-slate-200 bg-slate-50 text-slate-800 ring-rose-500/20 focus:border-emerald-500/50'">
                    <option value="">Tümü</option>
                    <option v-for="opt in filterOptionsWorst.renk_options" :key="opt" :value="opt">{{ opt }}</option>
                  </select>
                </div>
              </div>

              <!-- Worstseller Tablo -->
              <div class="relative min-h-[400px]">
                <!-- Loading Overlay -->
                <div v-if="loadingWorst" class="absolute inset-0 z-20 flex items-center justify-center rounded-xl backdrop-blur-[2px] transition-opacity duration-300" :class="isDarkMode ? 'bg-[#121722]/60' : 'bg-white/60'">
                  <div class="flex flex-col items-center gap-3">
                    <div class="h-10 w-10 animate-spin rounded-full border-4" :class="isDarkMode ? 'border-rose-500/20 border-t-rose-500' : 'border-rose-200 border-t-rose-600'"></div>
                    <span class="text-xs font-bold uppercase tracking-widest" :class="isDarkMode ? 'text-rose-400' : 'text-rose-600'">Veriler Güncelleniyor</span>
                  </div>
                </div>

                <div v-if="errorWorst" class="py-8 px-4 rounded-xl border text-sm" :class="isDarkMode ? 'border-rose-500/30 bg-rose-950/20 text-rose-200' : 'border-rose-200 bg-rose-50 text-rose-700'">
                  <p class="font-bold">⚠️ Worstseller hatası:</p>
                  <p class="mt-1 opacity-80">{{ errorWorst }}</p>
                </div>
                <div v-else-if="!loadingWorst && !worstsellers.length" class="py-12 text-center text-sm italic" :class="isDarkMode ? 'text-slate-500' : 'text-slate-400'">Veri bulunamadı.</div>
                <div v-else class="overflow-hidden rounded-xl border transition-all duration-500" :class="[isDarkMode ? 'border-white/5 bg-[#0b0f19]' : 'border-slate-200 bg-white', {'opacity-40 pointer-events-none': loadingWorst}]">
                  <div class="overflow-x-auto">
                    <table class="w-full min-w-[1000px] border-collapse text-left text-xs">
                      <thead>
                        <tr class="border-b text-[10px] font-bold uppercase tracking-wider" :class="isDarkMode ? 'border-white/10 bg-white/5 text-slate-400' : 'border-slate-100 bg-slate-50 text-slate-500'">
                          <th class="px-4 py-3.5">#</th>
                          <th class="px-4 py-3.5">Resim</th>
                          <th class="px-4 py-3.5">Stok Kodu</th>
                          <th class="px-4 py-3.5">Ürün Açıklama</th>
                          <th class="px-4 py-3.5 text-right font-bold" :class="isDarkMode ? 'text-rose-300' : 'text-rose-600'">Dönem Sonu Stok</th>
                          <th class="px-4 py-3.5 text-right">Satış Adedi</th>
                          <th class="px-4 py-3.5 text-right">Satış Oranı</th>
                          <th class="px-4 py-3.5 text-right">Cover</th>
                          <th class="px-4 py-3.5 text-right font-semibold" :class="isDarkMode ? 'text-violet-300' : 'text-violet-600'">GMROI</th>
                          <th class="px-4 py-3.5 text-right font-semibold" :class="isDarkMode ? 'text-rose-200' : 'text-rose-600'">Kar</th>
                        </tr>
                      </thead>
                      <tbody class="divide-y" :class="isDarkMode ? 'divide-white/5' : 'divide-slate-100'">
                        <tr v-for="(item, idx) in worstsellers" :key="item.stok_kodu" class="transition duration-150 group" :class="isDarkMode ? 'hover:bg-rose-500/5' : 'hover:bg-rose-50/50'">
                          <td class="px-4 py-3.5 font-medium" :class="isDarkMode ? 'text-slate-500' : 'text-slate-400'">{{ idx + 1 }}</td>
                          <td class="px-4 py-3.5">
                            <a :href="item.product_url || '#'" target="_blank" rel="noopener noreferrer" class="inline-block">
                              <div class="h-36 w-36 rounded-lg bg-white overflow-hidden ring-1 transition group-hover:scale-110" :class="isDarkMode ? 'ring-white/10' : 'ring-slate-200'">
                                <img :src="imgUrl(item.gorsel_link)" @error="onImgError" class="h-full w-full object-contain" alt="product" />
                              </div>
                            </a>
                          </td>
                          <td class="px-4 py-3.5 font-mono font-semibold uppercase" :class="isDarkMode ? 'text-rose-300' : 'text-rose-600'">{{ item.stok_kodu }}</td>
                          <td class="px-4 py-3.5 font-medium">
                            <div :class="isDarkMode ? 'text-slate-200' : 'text-slate-900'">{{ item.stok_aciklama }}</div>
                            <div class="text-[10px] mt-0.5 font-normal" :class="isDarkMode ? 'text-slate-500' : 'text-slate-500'">{{ item.marka_aciklama }} • {{ item.renk_aciklama }}</div>
                          </td>
                          <td class="px-4 py-3.5 text-right tabular-nums font-bold" :class="isDarkMode ? 'text-rose-300 bg-rose-500/5' : 'text-rose-600 bg-rose-50/50'">{{ formatNum(item.dss_miktari) }}</td>
                          <td class="px-4 py-3.5 text-right tabular-nums">{{ formatNum(item.satis_miktari) }}</td>
                          <td class="px-4 py-3.5 text-right tabular-nums" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">{{ formatPct(item.sell_through_pct) }}</td>
                          <td class="px-4 py-3.5 text-right tabular-nums font-medium" :class="item.periyot_cover_19 >= 100 ? (isDarkMode ? 'text-rose-400' : 'text-rose-600') : (isDarkMode ? 'text-slate-500' : 'text-slate-400')">
                            {{ item.periyot_cover_19 === 1000 ? '∞' : formatNum(item.periyot_cover_19) }}
                          </td>
                          <td class="px-4 py-3.5 text-right tabular-nums font-semibold" :class="isDarkMode ? 'text-violet-300' : 'text-violet-600'">{{ formatGmroi(item.gmroi) }}</td>
                          <td class="px-4 py-3.5 text-right tabular-nums font-semibold" :class="isDarkMode ? 'text-rose-200' : 'text-rose-600'">{{ formatMoney(item.toplam_kar) }}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </section>

          </div><!-- end v-show top10 -->

        </div>
      </main>

      <footer class="border-t px-6 py-4 shrink-0 transition-colors duration-500" :class="isDarkMode ? 'border-white/5 bg-[#070a12]' : 'border-slate-100 bg-white'">
        <div class="flex items-center justify-between">
          <p class="text-[10px] font-bold uppercase tracking-[0.2em]" :class="isDarkMode ? 'text-slate-600' : 'text-slate-400'">
            Analytics Engine v2.5 • Data Driven Retail Strategy
          </p>
          <div class="flex gap-4 text-[10px] font-mono" :class="isDarkMode ? 'text-slate-500' : 'text-slate-400'">
            <span>BS: {{ bestsellers.length }}</span>
            <span>WS: {{ worstsellers.length }}</span>
            <span v-if="errorBest" class="text-rose-400">BS Error!</span>
            <span v-if="errorWorst" class="text-rose-400">WS Error!</span>
          </div>
        </div>
      </footer>
    </div>

    <!-- HELP MODAL -->
    <div v-if="showHelp" class="fixed inset-0 z-50 flex items-center justify-center p-4 backdrop-blur-md bg-black/60">
      <div class="w-full max-w-4xl max-h-[85vh] overflow-hidden rounded-3xl border shadow-2xl flex flex-col transition-all duration-500" :class="isDarkMode ? 'border-white/10 bg-[#121722] shadow-black/50' : 'border-slate-200 bg-white shadow-slate-200/50'">
        <div class="flex items-center justify-between border-b p-6" :class="isDarkMode ? 'border-white/5' : 'border-slate-100'">
          <h3 class="text-xl font-bold flex items-center gap-2" :class="isDarkMode ? 'text-white' : 'text-slate-900'">
            <span class="text-sky-400">📖</span> Terimler ve Tanımlar
          </h3>
          <button @click="showHelp = false" class="h-10 w-10 rounded-full transition flex items-center justify-center" :class="isDarkMode ? 'hover:bg-white/5 text-slate-400' : 'hover:bg-slate-100 text-slate-500'">✕</button>
        </div>
        <div class="flex-1 overflow-y-auto p-6 space-y-8 scroll-smooth">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div v-for="category in [
              { title: 'Raporlar', color: 'text-sky-400', border: 'border-sky-500', terms: [
                { k: 'Bestseller', d: 'Satış hızı, karlılık ve cirosu yüksek olan haftalık yıldız ürünler.' },
                { k: 'Worstseller', d: 'Satış hızı düşük, stok riski yüksek haftalık verimsiz ürünler.' }
              ]},
              { title: 'Karlılık', color: 'text-emerald-400', border: 'border-emerald-500', terms: [
                { k: 'Brüt Kar', d: 'Ciro − SMM (KDV düşülmeden hesaplanır).' },
                { k: 'MU', d: 'Mark-up çarpanı (Ciro / Toplam SMM).' },
                { k: 'GMROI', d: 'Karın ortalama stok maliyetine oranı (Yıllıklandırılmış: Kar/Ort.Stok × 52).' }
              ]},
              { title: 'Stok & Satış', color: 'text-amber-400', border: 'border-amber-500', terms: [
                { k: 'Sell Through', d: 'Satış Oranı (Satış / [Satış + Stok]).' },
                { k: 'Cover', d: 'Mevcut stoğun kaç hafta yeteceği (Stok / Satış).' },
                { k: 'DBS / DSS', d: 'Dönem başı stok / Dönem sonu stok adedi.' }
              ]},
              { title: 'Sınıflandırma', color: 'text-purple-400', border: 'border-purple-500', terms: [
                { k: 'Sezon', d: '25F (Kış/Güz), 25S (Yaz/Bahar) kodlaması.' },
                { k: 'Raf Ömrü', d: 'Ürünün mağaza stoğunda kalarak satış gördüğü gün sayısı.' }
              ]}
            ]" :key="category.title" class="space-y-4">
              <h4 class="text-sm font-bold uppercase tracking-widest border-l-2 pl-3" :class="[category.color, category.border]">{{ category.title }}</h4>
              <div class="space-y-3 text-sm">
                <p v-for="t in category.terms" :key="t.k"><strong :class="isDarkMode ? 'text-white' : 'text-slate-900'">{{ t.k }}:</strong> <span :class="isDarkMode ? 'text-slate-300' : 'text-slate-600'">{{ t.d }}</span></p>
              </div>
            </div>
          </div>
        </div>
        <div class="p-6 transition-colors" :class="isDarkMode ? 'bg-white/2' : 'bg-slate-50'">
          <button @click="showHelp = false" class="w-full py-3 rounded-xl font-bold text-white transition shadow-lg shadow-sky-600/20" :class="isDarkMode ? 'bg-sky-600 hover:bg-sky-500' : 'bg-sky-600 hover:bg-sky-700'">Anladım</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

body {
  font-family: 'Inter', sans-serif;
  margin: 0;
}

::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: rgba(128, 128, 128, 0.2);
  border-radius: 10px;
  border: 2px solid transparent;
  background-clip: padding-box;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(128, 128, 128, 0.4);
}

/* Animations */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
