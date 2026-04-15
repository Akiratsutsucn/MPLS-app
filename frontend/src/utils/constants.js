export const PHASES = [
  { key: 'grading', label: '定级', color: '#E6A23C', bgColor: '#fdf6ec', icon: '📌' },
  { key: 'filing', label: '备案', color: '#409EFF', bgColor: '#ecf5ff', icon: '📝' },
  { key: 'rectification', label: '建设整改', color: '#67C23A', bgColor: '#f0f9eb', icon: '🔧' },
  { key: 'evaluation', label: '等级测评', color: '#F56C6C', bgColor: '#fef0f0', icon: '🔍' },
  { key: 'supervision', label: '监督检查', color: '#909399', bgColor: '#f4f4f5', icon: '✅' },
]

export const LEVELS = { 1: '一级', 2: '二级', 3: '三级', 4: '四级', 5: '五级' }

export const PHASE_MAP = Object.fromEntries(PHASES.map(p => [p.key, p]))
