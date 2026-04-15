export const PHASES = [
  { key: 'preparation', label: '准备', color: '#E6A23C', bgColor: '#fdf6ec', icon: '📋' },
  { key: 'self_assessment', label: '自测评', color: '#409EFF', bgColor: '#ecf5ff', icon: '🔍' },
  { key: 'rectification', label: '整改', color: '#67C23A', bgColor: '#f0f9eb', icon: '🔧' },
  { key: 'formal_evaluation', label: '正式测评', color: '#F56C6C', bgColor: '#fef0f0', icon: '📝' },
  { key: 'filing', label: '备案', color: '#909399', bgColor: '#f4f4f5', icon: '📌' },
  { key: 'reporting', label: '报告编制', color: '#8B5CF6', bgColor: '#f5f3ff', icon: '📄' },
]

export const LEVELS = { 1: '一级', 2: '二级', 3: '三级', 4: '四级', 5: '五级' }

export const PHASE_MAP = Object.fromEntries(PHASES.map(p => [p.key, p]))
