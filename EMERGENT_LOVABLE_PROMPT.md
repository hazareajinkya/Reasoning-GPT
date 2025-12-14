# Prompt for Emergent Lovable Site - Reasoning GPT UI

## Task
Redesign the UI for "Reasoning GPT" - an educational CAT DILR problem solver. Make it modern, sleek, and visually stunning while maintaining excellent usability.

## Current App Structure
- **Header**: Title "Reasoning GPT" + subtitle "learn how to develop easy approach to any CAT DILR problem"
- **Main Content Area**: Question input textarea + "Get Explanation" button + Solution display with 4 tabs
- **Sidebar**: History panel showing past questions
- **Theme**: Dark (black background)

## Design Requirements

### Visual Style
- Modern, sleek, professional design
- Dark theme with black/dark gray backgrounds
- Accent colors: Blue for primary actions, Green for success, Red for errors
- Subtle gradients and shadows for depth
- Smooth animations and transitions (200-300ms)
- Rounded corners (rounded-lg, rounded-xl)
- Generous spacing and padding

### Header Section
- Large, bold "Reasoning GPT" title (white text, 4xl-5xl)
- Subtitle: "learn how to develop easy approach to any CAT DILR problem" (gray-300, text-lg)
- Centered layout
- Add subtle visual interest (gradient, accent color, or icon)

### Question Input Card
- Large, prominent textarea (6+ rows)
- Modern rounded design with focus ring
- "Get Explanation" button - eye-catching but professional
- Loading state with spinner
- Dark gray card background with subtle border

### Solution Display
- **Tabs**: Modern tab design with smooth transitions
  - 4 tabs: Direct Answer, Step-by-Step, Intuitive, Shortcut
  - Active tab highlighted with accent color
  - Smooth hover effects
- **Content Area**: 
  - Scrollable with max-height
  - Well-spaced progressive tables
  - Clear typography for explanations
  - Good line height for readability

### History Sidebar
- Clean, minimal card design
- Clickable history items with hover effects
- Question preview (truncated with ellipsis)
- Timestamp display
- Clear history button at bottom

### Responsive Design
- Mobile-first approach
- Stack layout on mobile
- Touch-friendly button sizes
- Proper breakpoints (sm, md, lg)

### Key Improvements Needed
1. Better visual hierarchy - make header more prominent
2. Modern card designs with better shadows
3. Improved table spacing and readability
4. Smooth tab transitions
5. Better color accents throughout
6. Enhanced typography (sizes, line heights)
7. Polished loading and error states

## Technical Details
- Framework: Next.js (React) + TypeScript
- Styling: Tailwind CSS
- Current container: `container mx-auto px-4 py-8 max-w-6xl`
- Grid: `grid grid-cols-1 lg:grid-cols-3 gap-6`

## Deliverable
Create a beautiful, modern UI that is:
- Visually stunning and professional
- Highly readable and accessible
- Smooth and responsive
- Maintains dark theme consistency
- Makes learning enjoyable

Focus on creating a "wow" factor while keeping usability excellent.

