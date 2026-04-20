# ARIA Design Tokens

> Single source of truth for all colors, typography, spacing, and component conventions.
> Every segment of the build references this file.

---

## Color Palette

### Brand

| Token | Hex | Usage |
|---|---|---|
| `brand-primary` | `#4F46E5` | Primary actions, active states, links — deep indigo |
| `brand-primary-hover` | `#4338CA` | Hover state on primary buttons |
| `brand-primary-light` | `#EEF2FF` | Backgrounds, tinted surfaces |
| `brand-accent` | `#6366F1` | Gradient partner, secondary brand moments |

### Semantic — Evaluation Outcomes

| Token | Hex | Usage |
|---|---|---|
| `outcome-pass` | `#10B981` | Proceed recommendation, pass badges — emerald |
| `outcome-pass-light` | `#D1FAE5` | Pass badge background |
| `outcome-fail` | `#F43F5E` | Abandon/rejected recommendation — rose |
| `outcome-fail-light` | `#FFE4E6` | Fail badge background |
| `outcome-warn` | `#F59E0B` | Modify / conditional recommendation — amber |
| `outcome-warn-light` | `#FEF3C7` | Warn badge background |
| `outcome-pause` | `#8B5CF6` | Pause recommendation — violet |
| `outcome-pause-light` | `#EDE9FE` | Pause badge background |

### Status — Pipeline States

| Token | Hex | Usage |
|---|---|---|
| `status-queued` | `#6B7280` | Queued state — gray |
| `status-queued-bg` | `#F3F4F6` | Queued badge background |
| `status-running` | `#3B82F6` | Running / in-progress — blue (animated pulse) |
| `status-running-bg` | `#DBEAFE` | Running badge background |
| `status-complete` | `#10B981` | Complete — green |
| `status-complete-bg` | `#D1FAE5` | Complete badge background |
| `status-failed` | `#EF4444` | Failed — red |
| `status-failed-bg` | `#FEE2E2` | Failed badge background |
| `status-conditional` | `#F59E0B` | Conditional / warning — amber |
| `status-conditional-bg` | `#FEF3C7` | Conditional badge background |

### Neutrals

| Token | Hex | Usage |
|---|---|---|
| `neutral-50` | `#F9FAFB` | Page background |
| `neutral-100` | `#F3F4F6` | Surface / card background |
| `neutral-200` | `#E5E7EB` | Borders, dividers |
| `neutral-300` | `#D1D5DB` | Disabled input borders |
| `neutral-400` | `#9CA3AF` | Placeholder text |
| `neutral-500` | `#6B7280` | Secondary / muted text |
| `neutral-600` | `#4B5563` | Body text secondary |
| `neutral-700` | `#374151` | Body text primary |
| `neutral-800` | `#1F2937` | Headings |
| `neutral-900` | `#111827` | High-contrast text / dark backgrounds |

### Surface & Background

| Token | Value | Usage |
|---|---|---|
| `bg-page` | `neutral-50` (`#F9FAFB`) | Main page background |
| `bg-surface` | `#FFFFFF` | Cards, modals, panels |
| `bg-surface-raised` | `neutral-100` | Nested surfaces, sidebars |
| `bg-overlay` | `rgba(0,0,0,0.5)` | Modal backdrop |

### LLM Brand Colors (Agent badges)

| Token | Hex | LLM |
|---|---|---|
| `llm-claude` | `#D97706` | Anthropic Claude — amber |
| `llm-claude-bg` | `#FEF3C7` | Claude badge background |
| `llm-openai` | `#10B981` | OpenAI GPT-4o — emerald |
| `llm-openai-bg` | `#D1FAE5` | OpenAI badge background |
| `llm-gemini` | `#3B82F6` | Google Gemini — blue |
| `llm-gemini-bg` | `#DBEAFE` | Gemini badge background |

---

## Typography

### Font Families

| Token | Value | Usage |
|---|---|---|
| `font-sans` | `Inter, ui-sans-serif, system-ui` | All UI text — headings, body, labels |
| `font-mono` | `'Geist Mono', ui-monospace, monospace` | Scores, numbers, code snippets |

### Type Scale

| Token | Size | Line Height | Weight | Usage |
|---|---|---|---|---|
| `text-h1` | `2.25rem` (36px) | `1.2` | `700` | Page titles (landing, report header) |
| `text-h2` | `1.875rem` (30px) | `1.25` | `700` | Section headings |
| `text-h3` | `1.5rem` (24px) | `1.3` | `600` | Card headings, sidebar section titles |
| `text-h4` | `1.25rem` (20px) | `1.4` | `600` | Sub-section headings, accordion titles |
| `text-body-lg` | `1.125rem` (18px) | `1.6` | `400` | Primary body text, descriptions |
| `text-body` | `1rem` (16px) | `1.6` | `400` | Default body text |
| `text-body-sm` | `0.875rem` (14px) | `1.5` | `400` | Secondary text, table cells, labels |
| `text-caption` | `0.75rem` (12px) | `1.4` | `400` | Timestamps, helper text, footnotes |
| `text-score` | `2rem` (32px) | `1` | `700` | Score rings, stat cards — uses `font-mono` |
| `text-score-sm` | `1.25rem` (20px) | `1` | `600` | Small score displays — uses `font-mono` |

---

## Spacing Scale

Uses Tailwind's default 4px base unit. Custom additions:

| Token | Value | Usage |
|---|---|---|
| `spacing-0` | `0px` | — |
| `spacing-1` | `4px` | Tight gaps (icon + label) |
| `spacing-2` | `8px` | Small padding, badge inner |
| `spacing-3` | `12px` | Compact element padding |
| `spacing-4` | `16px` | Default inner padding |
| `spacing-5` | `20px` | Card padding (mobile) |
| `spacing-6` | `24px` | Card padding (desktop), section gaps |
| `spacing-8` | `32px` | Component separation |
| `spacing-10` | `40px` | Section padding |
| `spacing-12` | `48px` | Large section gaps |
| `spacing-16` | `64px` | Page-level vertical rhythm |
| `spacing-20` | `80px` | Hero / landing sections |
| `spacing-24` | `96px` | Large hero padding |

---

## Border Radius

| Token | Value | Usage |
|---|---|---|
| `radius-sm` | `4px` | Badges, tags, small chips |
| `radius-md` | `8px` | Buttons, inputs, small cards |
| `radius-lg` | `12px` | Cards, panels, modals |
| `radius-xl` | `16px` | Large cards, drawers |
| `radius-2xl` | `24px` | Hero cards, feature cards |
| `radius-full` | `9999px` | Pills, avatar circles, progress bars |

---

## Shadows

| Token | Value | Usage |
|---|---|---|
| `shadow-sm` | `0 1px 2px rgba(0,0,0,0.05)` | Subtle card lift |
| `shadow-md` | `0 4px 6px rgba(0,0,0,0.07)` | Card hover, dropdowns |
| `shadow-lg` | `0 10px 15px rgba(0,0,0,0.10)` | Modals, floating panels |
| `shadow-xl` | `0 20px 25px rgba(0,0,0,0.12)` | Popovers, elevated dialogs |

---

## Icon Set

**Library:** [Lucide React](https://lucide.dev)

| Icon | Token Name | Usage |
|---|---|---|
| `LayoutDashboard` | — | Dashboard nav |
| `Database` | — | Knowledge Base nav |
| `Lightbulb` | — | Evaluations nav |
| `Settings` | — | Settings nav |
| `Upload` | — | File upload |
| `FileText` | — | Document item |
| `CheckCircle2` | — | Complete status |
| `XCircle` | — | Failed status |
| `Clock` | — | Queued / pending |
| `Loader2` | — | Running (animated spin) |
| `AlertTriangle` | — | Conditional / warning |
| `ChevronRight` | — | Expand / navigate |
| `ChevronDown` | — | Collapse |
| `Download` | — | PDF download |
| `Trash2` | — | Delete action |
| `Plus` | — | Add / new |
| `Users` | — | Team / HR |
| `DollarSign` | — | Finance |
| `TrendingUp` | — | Sales / Market |
| `Cpu` | — | Development / Tech |
| `Palette` | — | Design |
| `Megaphone` | — | Marketing |
| `Globe` | — | Market Research |
| `ShieldCheck` | — | Orchestrator / Policy |
| `BarChart2` | — | Charts / Reports |
| `Radar` | — | Feasibility Radar |
| `Zap` | — | Live / Real-time |

Icon size conventions:
- **Nav icons:** `20px` (w-5 h-5)
- **Button icons:** `16px` (w-4 h-4)
- **Status icons:** `20px` (w-5 h-5)
- **Large decorative icons:** `32px` (w-8 h-8)

---

## Component Inventory

### Buttons

| Variant | Background | Text | Border | Use Case |
|---|---|---|---|---|
| `primary` | `brand-primary` | white | none | Main CTA ("Evaluate", "Upload") |
| `secondary` | white | `brand-primary` | `brand-primary` | Secondary actions |
| `ghost` | transparent | `neutral-700` | none | Tertiary actions, nav items |
| `destructive` | `outcome-fail` | white | none | Delete, abandon |
| `outline` | transparent | `neutral-600` | `neutral-300` | Neutral secondary |

Sizes: `sm` (h-8, px-3, text-sm) · `md` (h-10, px-4, text-base) · `lg` (h-12, px-6, text-lg)

### Badges

| Variant | Background | Text | Use Case |
|---|---|---|---|
| `proceed` | `outcome-pass-light` | `outcome-pass` | Proceed recommendation |
| `abandon` | `outcome-fail-light` | `outcome-fail` | Abandon recommendation |
| `modify` | `outcome-warn-light` | `outcome-warn` | Modify recommendation |
| `pause` | `outcome-pause-light` | `outcome-pause` | Pause recommendation |
| `queued` | `status-queued-bg` | `status-queued` | Queued pipeline state |
| `running` | `status-running-bg` | `status-running` | Running pipeline state |
| `complete` | `status-complete-bg` | `status-complete` | Complete pipeline state |
| `failed` | `status-failed-bg` | `status-failed` | Failed pipeline state |
| `conditional` | `status-conditional-bg` | `status-conditional` | Conditional pipeline state |
| `claude` | `llm-claude-bg` | `llm-claude` | Claude LLM badge |
| `openai` | `llm-openai-bg` | `llm-openai` | GPT-4o LLM badge |
| `gemini` | `llm-gemini-bg` | `llm-gemini` | Gemini LLM badge |

### Cards

- **Base Card:** white bg, `shadow-sm`, `radius-lg`, `p-6`
- **Stat Card:** base + large mono number + trend arrow
- **Agent Card:** base + agent avatar + LLM badge + score ring (when complete) + pulse animation (when running)
- **Feature Card:** `bg-surface-raised`, icon + title + description

### Other Components

| Component | Notes |
|---|---|
| `Modal / Dialog` | Centered, `radius-xl`, `shadow-xl`, max-w-lg/2xl, backdrop overlay |
| `Table` | Bordered rows, `text-body-sm`, hover state `neutral-50`, sticky header |
| `Tabs` | Underline style, active tab `brand-primary` border + text |
| `Progress Bar` | `radius-full`, animated fill, uses status colors |
| `Radar Chart` | Recharts `RadarChart`, 6 axes, `brand-primary` fill with 30% opacity |
| `Score Ring` | SVG circle, stroke = status/outcome color, center mono number |
| `Stepper` | Vertical list, icon per step (pending/running/complete/failed), connector line |
| `Uploader` | Dashed border `neutral-300`, dashed hover `brand-primary`, drag-active highlight |
| `Sidebar Nav` | Fixed left, `bg-surface-raised`, icon + label, active `brand-primary-light` bg |
| `Drawer` | Slides from right, 480px wide, `shadow-xl`, overlay backdrop |

---

## Status Color System (Summary)

| Status | Color Token | Hex | Animation |
|---|---|---|---|
| `queued` | `status-queued` | `#6B7280` | None |
| `running` | `status-running` | `#3B82F6` | `animate-pulse` on icon |
| `complete` | `status-complete` | `#10B981` | None |
| `failed` | `status-failed` | `#EF4444` | None |
| `conditional` | `status-conditional` | `#F59E0B` | None |

---

## Tailwind Class Naming Conventions

- Colors are referenced as `text-indigo-600`, `bg-indigo-50` using Tailwind's extended palette configured in `tailwind.config.ts`
- All custom tokens are mapped to named keys in `tailwind.config.ts` (see that file)
- Status colors use the `status-*` key group; outcome colors use `outcome-*`
- Typography classes follow Tailwind's standard `text-` prefix
