# UI Design Prompt for Reasoning GPT

## Project Overview
Create a modern, sleek, and professional UI for "Reasoning GPT" - an educational tool that helps students learn how to solve CAT DILR (Data Interpretation & Logical Reasoning) problems step-by-step.

## Current Structure
The app has:
- A dark theme (black background)
- Main content area (left 2/3) with question input and solution display
- History sidebar (right 1/3)
- Four solution tabs: Direct Answer, Step-by-Step, Intuitive, Shortcut
- Progressive tables showing step-by-step problem solving

## Design Requirements

### 1. Header Section
- **Title**: "Reasoning GPT" (large, bold, white text)
- **Subtitle**: "learn how to develop easy approach to any CAT DILR problem" (gray text, smaller)
- Should be centered and prominent
- Add subtle gradient or accent color for visual interest

### 2. Main Layout
- **Container**: Max width 6xl, centered, with padding
- **Grid Layout**: 2-column on large screens (2/3 main, 1/3 sidebar), single column on mobile
- **Spacing**: Generous spacing between sections (gap-6 or more)

### 3. Question Input Section
- Large, prominent textarea for question input
- Modern, rounded design with focus states
- "Get Explanation" button - should be eye-catching but professional
- Loading state with spinner animation
- Placeholder text should be helpful and clear

### 4. Solution Display
- **Tabs**: Modern tab design with smooth transitions
- **Active Tab**: Highlighted with accent color (blue/green)
- **Content Area**: Scrollable, well-spaced
- **Tables**: Properly formatted with good spacing between progressive tables
- **Explanations**: Clear typography, good line height, readable

### 5. History Sidebar
- Clean, minimal design
- Each history item should be clickable
- Show question preview (truncated)
- Timestamp display
- Clear history button

### 6. Color Scheme
- **Background**: Dark (black or very dark gray)
- **Primary Text**: White/light gray
- **Accent Colors**: 
  - Blue for primary actions and active states
  - Green for success/positive states
  - Red for errors
- **Borders**: Subtle gray borders for separation
- **Cards/Sections**: Dark gray backgrounds with subtle borders

### 7. Typography
- **Headings**: Bold, large, clear hierarchy
- **Body Text**: Readable, good line height (1.6-1.8)
- **Code/Tables**: Monospace font for tables
- **Font Sizes**: Responsive, larger on desktop

### 8. Interactive Elements
- Smooth hover effects
- Clear focus states for accessibility
- Loading states with animations
- Smooth transitions (200-300ms)
- Button states: hover, active, disabled

### 9. Responsive Design
- Mobile-first approach
- Breakpoints: sm (640px), md (768px), lg (1024px)
- Stack layout on mobile
- Touch-friendly button sizes on mobile

### 10. Visual Enhancements
- Subtle shadows for depth
- Rounded corners (rounded-lg, rounded-xl)
- Gradient accents (optional, subtle)
- Smooth animations for state changes
- Proper spacing and padding throughout

## Specific Improvements Needed

1. **Better Visual Hierarchy**: Make the header more prominent
2. **Modern Card Design**: Update the question input and solution cards with better shadows and borders
3. **Table Styling**: Ensure tables are well-spaced, readable, and visually appealing
4. **Tab Design**: Modern tab interface with smooth transitions
5. **Spacing**: More generous spacing between sections
6. **Color Accents**: Add subtle color accents for visual interest
7. **Typography**: Improve font sizes and line heights for better readability
8. **Loading States**: Better loading animations and feedback
9. **Error States**: Clear, user-friendly error messages
10. **History Panel**: More polished design with better item cards

## Technical Stack
- Next.js (React)
- Tailwind CSS
- TypeScript
- Dark theme throughout

## Key Components to Style
1. Header (title + subtitle)
2. QuestionInput component
3. SolutionDisplay component (tabs + content)
4. HistoryPanel component
5. Error messages
6. Loading states

## Design Inspiration
- Modern educational platforms (Khan Academy, Coursera)
- Clean, minimal design
- Focus on readability and usability
- Professional but approachable
- Dark theme with good contrast

## Deliverables
Create a beautiful, modern UI that:
- Is visually appealing and professional
- Maintains excellent readability
- Has smooth interactions and animations
- Works perfectly on mobile and desktop
- Follows the dark theme consistently
- Makes the learning experience enjoyable


