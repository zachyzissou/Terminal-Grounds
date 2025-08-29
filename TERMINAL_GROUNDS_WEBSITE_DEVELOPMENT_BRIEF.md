# Terminal Grounds Website Development Brief
## Complete Implementation Specification for bloom.slurpgg.net

**Document Version**: 1.0  
**Date**: August 29, 2025  
**Target Audience**: External Website Development Teams  
**Project Codename**: Terminal Grounds (Internal) / Bloom (Public Brand)  

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Technical Specifications](#technical-specifications)
3. [Content Strategy & Copy](#content-strategy--copy)
4. [Asset Implementation Guide](#asset-implementation-guide)
5. [Interactive Features Specification](#interactive-features-specification)
6. [Site Architecture](#site-architecture)
7. [Implementation Timeline](#implementation-timeline)
8. [Brand Guidelines](#brand-guidelines)
9. [Quality Assurance Requirements](#quality-assurance-requirements)
10. [Success Metrics](#success-metrics)

---

## Executive Summary

Terminal Grounds is a **territorial warfare extraction shooter** set in a post-cascade world where factions compete for alien technology within the quarantined Bloom zone. The website must convey grounded military desperation, technological stratification, and high-stakes extraction gameplay while serving multiple audiences from casual gamers to hardcore tactical enthusiasts.

### Core Value Propositions
- **Grounded Tactical Realism**: Authentic military enhancement with logistics-driven gameplay
- **Faction-Driven Conflict**: Seven distinct factions with unique philosophies and territorial control
- **Technology Tiers**: Clear progression from Field → Splice → Monolith grade equipment
- **Extraction Tension**: High-stakes salvage missions with meaningful consequences

### Primary Goals
1. **Pre-Registration Conversion**: Drive sign-ups with faction preference selection
2. **Community Building**: Foster faction loyalty and player-generated content
3. **Technical Communication**: Explain complex systems accessibly
4. **Brand Positioning**: Establish Bloom as premium extraction shooter experience

---

## Technical Specifications

### Performance Requirements
- **Page Load Speed**: < 3 seconds initial load, < 1.5 seconds subsequent pages
- **Core Web Vitals**: LCP < 2.5s, FID < 100ms, CLS < 0.1
- **Mobile Performance**: 90+ PageSpeed Insights score on mobile
- **Accessibility**: WCAG 2.1 AA compliance minimum

### Responsive Breakpoints
```css
/* Mobile First Approach */
Base: 320px - 767px (Mobile)
Tablet: 768px - 1023px  
Desktop: 1024px - 1439px
Large Desktop: 1440px+

/* Critical Asset Breakpoints */
Hero Images: 
- Mobile: 414px wide (2x for retina)
- Tablet: 768px wide
- Desktop: 1920px wide
```

### Image Optimization Standards
```
Hero Images: WebP primary, PNG fallback
- Desktop: 1920x1080 (compressed to <500KB)
- Tablet: 768x432 (compressed to <200KB)  
- Mobile: 414x233 (compressed to <100KB)

Faction Emblems: SVG primary, PNG fallback
- Base size: 1024x1024
- Compressed PNG: <50KB each

Environmental Assets: WebP with JPEG fallback
- Gallery: 1536x864 source, responsive sizing
- Thumbnails: 320x180 (compressed to <25KB)

Logo Assets: SVG primary for scalability
- Fallback PNG at 2x resolution for each breakpoint
```

### Browser Support Matrix
- **Primary Support**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Secondary Support**: Chrome 80+, Firefox 80+, Safari 13+
- **Legacy Graceful Degradation**: IE11 (functional but no advanced features)

### Technical Stack Recommendations
```
Frontend: React 18+ or Vue 3+ (component-based for faction content)
Build System: Vite or Webpack 5+ with tree-shaking
CSS Framework: Tailwind CSS 3+ (utility-first for rapid iteration)
Animation: Framer Motion or GSAP for hero animations
Image Processing: Sharp.js for build-time optimization
CDN: Cloudflare or AWS CloudFront for global delivery
```

### Asset Delivery Requirements
```
CDN Structure:
/assets/images/
├── heroes/          # Hero section backgrounds
├── factions/        # Faction-specific assets
│   ├── emblems/     # SVG emblems with PNG fallbacks
│   ├── concepts/    # Concept art galleries
│   └── colors/      # Faction color swatches
├── environments/    # Environmental concept art
├── logos/          # Bloom branding assets
└── ui/             # Interface elements

Naming Convention: [category]_[faction]_[variant]_[size].[ext]
Example: emblem_directorate_main_1024.png
```

---

## Content Strategy & Copy

### Primary Audience Segments

#### **Casual Shooters (40%)**
- **Motivation**: Fun, accessible tactical gameplay
- **Concerns**: Learning curve, time investment
- **Decision Drivers**: Visual appeal, faction identity, social features
- **Copy Strategy**: Emphasize accessibility within depth

#### **Extraction Shooter Veterans (35%)**  
- **Motivation**: Meaningful progression, high-stakes gameplay
- **Concerns**: Pay-to-win mechanics, server stability
- **Decision Drivers**: Skill ceiling, risk/reward balance, competitive integrity
- **Copy Strategy**: Highlight tactical depth and fair progression

#### **Tactical Enthusiasts (25%)**
- **Motivation**: Authentic military simulation, strategic depth  
- **Concerns**: Arcade elements, unrealistic mechanics
- **Decision Drivers**: Weapon handling, logistics systems, faction authenticity
- **Copy Strategy**: Emphasize grounded militarism and realistic enhancement

### Hero Section Copy Options

#### **Safe Option (Broad Appeal)**
**Headline**: "Master the Extraction"  
**Subheading**: "Command your faction. Salvage alien technology. Extract under fire."  
**Body**: "In the quarantined Bloom zone, seven factions wage territorial warfare over reality-bending Harvester technology. Lead tactical operations, upgrade through three equipment tiers, and extract with game-changing artifacts—or lose everything trying."  
**CTA**: "Choose Your Faction"

#### **Bold Option (Confident Positioning)**
**Headline**: "Logistics is Drama. Extraction is Everything."  
**Subheading**: "A grounded tactical shooter where alien technology changes the rules of warfare."  
**Body**: "Six months after the Cascade, the IEZ bleeds alien tech and faction blood. Master Field-grade reliability, risk Splice-grade power, or gamble everything on Monolith artifacts that rewrite reality. Every extraction tells a story. Every loss reshapes the war."  
**CTA**: "Join the War for Tomorrow"

#### **Experimental Option (Genre-Disrupting)**
**Headline**: "Your Supply Chain Is Your Lifeline"  
**Subheading**: "The extraction shooter that makes every bullet count."  
**Body**: "Forget endless ammunition. In Bloom, you fight with what you carry, salvage what you find, and extract what you can defend. Choose from seven battle-tested factions, each with unique supply chains, territorial advantages, and paths to technological supremacy."  
**CTA**: "Supply Up. Ship Out."

### Faction Page Copy Framework

Each faction requires:
- **Philosophy Statement** (1-2 sentences capturing faction worldview)
- **Territory Description** (2-3 sentences describing their domain)
- **Technology Focus** (1-2 sentences explaining their tech preferences)
- **Gameplay Identity** (2-3 sentences translating lore into gameplay advantages)
- **Signature Quote** (Memorable faction motto or battle cry)

### SEO Content Strategy

#### **Primary Keywords**
- tactical shooter
- extraction shooter  
- faction warfare
- alien technology game
- territorial control shooter

#### **Long-tail Keywords**
- military extraction shooter 2025
- faction-based tactical shooter
- alien tech salvage game
- territorial warfare FPS
- realistic tactical enhancement

#### **Content Pillars for Blog/News**
1. **Faction Spotlight Series**: Deep dives into faction lore, tactics, and territories
2. **Technology Explained**: How Field/Splice/Monolith tiers create gameplay depth
3. **Developer Insights**: Behind-the-scenes development stories and technical achievements  
4. **Community Highlights**: Player stories, faction artwork, tactical guides
5. **World Building**: Environmental storytelling and post-Cascade world expansion

---

## Asset Implementation Guide

### Source Asset Locations (Terminal Grounds Project)

#### **Production-Ready Assets**
```
Base Path: C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API\output\

01_PRODUCTION_READY/
├── environments/
│   ├── corporate/
│   │   ├── TG_ENV_Corporate_Lobby_CleanSciFi_v01.png (1536x864)
│   │   └── TG_ENV_Corporate_Lobby_GrittyRealism_v01.png (1536x864)
│   ├── industrial/
│   │   ├── TG_PERFECT_IEZ_Facility_Interior_Clean_SciFi_Detail_Dramatic_00001_.png
│   │   ├── TG_PERFECT_Security_Checkpoint_Clean_SciFi_Perspective_Atmospheric_00001_.png
│   │   └── TG_PERFECT_Tech_Wastes_Exterior_Clean_SciFi_Perspective_Atmospheric_00001_.png
│   ├── underground/
│   │   ├── TG_ENV_Metro_Corridor_CleanSciFi_v01.png (High quality tunnel system)
│   │   ├── TG_ENV_Metro_Metro_Maintenance_Corridor_CleanSciFi_v01.png
│   │   └── TG_ENV_Underground_Bunker_CleanSciFi_v01.png
│   └── wasteland/
│       ├── TG_PERFECT_Tech_Wastes_Exterior_Clean_SciFi_Perspective_Atmospheric_00001_.png
│       └── TG_PERFECT_Tech_Wastes_Exterior_Gritty_Realism_Perspective_Atmospheric_00001_.png

├── factions/
│   ├── emblems/
│   │   ├── TG_Enhanced_Emblem_Directorate_00001_.png (1024x1024)
│   │   ├── TG_Enhanced_Emblem_Free77_00001_.png (1024x1024)
│   │   ├── TG_Enhanced_Emblem_IronScavengers_00001_.png (1024x1024)
│   │   ├── TG_Enhanced_Emblem_CorporateHegemony_00001_.png (1024x1024)
│   │   ├── TG_Enhanced_Emblem_NomadClans_00001_.png (1024x1024)
│   │   ├── TG_Enhanced_Emblem_ArchiveKeepers_00002_.png (1024x1024)
│   │   └── TG_Enhanced_Emblem_CivicWardens_00001_.png (1024x1024)
│   ├── vehicles/
│   │   ├── TG_FIXED_Vehicle_Directorate_00001_.png (Faction-specific vehicles)
│   │   ├── TG_FIXED_Vehicle_IronScavengers_00001_.png
│   │   └── [Additional faction vehicles available]
│   └── characters/
│       ├── TG_Character_Directorate_Trooper_00001_.png (Faction operators)
│       ├── TG_Character_IronScavengers_Raider_00001_.png
│       └── [Additional faction characters]

├── weapons/
│   ├── TG_Weapon_Sharp_Directorate_MG_00001_.png (High-detail weapon concepts)
│   ├── TG_Weapon_Sharp_IronScavengers_Rifle_00001_.png
│   └── [Complete weapon library available]

└── ui_elements/
    ├── TG_UI_Directorate_HUD_00001_.png (Faction-themed UI concepts)
    ├── TG_UI_IronScavengers_HUD_00001_.png
    └── [All faction UI themes available]
```

#### **Faction Color Palettes (from Data\Tables\Factions.csv)**
```css
/* Faction Brand Colors - Ready for CSS Implementation */

.directorate {
  --primary: #161A1D;    /* Gunmetal Authority */
  --secondary: #2E4053;  /* Navy Command */
  --accent: #85929E;     /* Steel Highlight */
}

.iron-scavengers {
  --primary: #7F8C8D;    /* Weathered Metal */
  --secondary: #D35400;  /* Trophy Orange */
  --accent: #F39C12;     /* Salvage Gold */
}

.seventy-seven {
  --primary: #34495E;    /* Professional Gray */
  --secondary: #BDC3C7;  /* Contract Silver */
  --accent: #95A5A6;     /* Neutral Tone */
}

.corporate-hegemony {
  --primary: #0C0F12;    /* Corporate Black */
  --secondary: #00C2FF;  /* Holographic Blue */
  --accent: #3498DB;     /* Brand Cyan */
}

.nomad-clans {
  --primary: #6E2C00;    /* Desert Bronze */
  --secondary: #AF601A;  /* Sun-bleached Orange */
  --accent: #E67E22;     /* Road Marker */
}

.archive-keepers {
  --primary: #2C3E50;    /* Archive Deep Blue */
  --secondary: #8E44AD;  /* Ancient Purple */
  --accent: #9B59B6;     /* Knowledge Violet */
}

.civic-wardens {
  --primary: #145A32;    /* Forest Green */
  --secondary: #27AE60;  /* Safety Green */
  --accent: #2ECC71;     /* Warden Highlight */
}
```

#### **Bloom Branding Assets**
```
Base Path: C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API\output\02_CHIEF_ART_DIRECTOR\game_branding\

Expected Files (pending generation completion):
├── BLOOM_LOGO_Main_v01.png (Primary logo - 2048x2048)
├── BLOOM_LOGO_Horizontal_v01.png (Header logo - 3072x1024)  
├── BLOOM_LOGO_Icon_v01.png (App icon - 1024x1024)
├── BLOOM_LOGO_Wordmark_v01.png (Text only - 2048x512)
├── BLOOM_LOGO_Monochrome_v01.png (Single color - 2048x2048)
└── BLOOM_LOGO_Emblem_v01.png (Symbol only - 1024x1024)

Usage Priority:
1. Header/Navigation: Horizontal version
2. Hero Section: Main logo (transparent background)
3. Favicon/Mobile: Icon version (optimized for 32px display)
4. Footer: Wordmark or monochrome
5. Social Media: Emblem (square format)
```

### Asset Optimization Pipeline
```bash
# Required Optimizations for Web Deployment

# 1. Convert to WebP with fallbacks
for file in *.png; do
  cwebp -q 85 "$file" -o "${file%.png}.webp"
done

# 2. Generate responsive versions
convert original.png -resize 1920x1080 desktop.png
convert original.png -resize 768x432 tablet.png  
convert original.png -resize 414x233 mobile.png

# 3. Optimize PNG fallbacks
pngquant --quality=65-85 --ext .png --force *.png

# 4. Generate 2x retina versions
convert desktop.png -resize 200% desktop@2x.png
```

---

## Interactive Features Specification

### Faction Selection System

#### **Visual Interface Requirements**
```
Layout: Hexagonal faction grid with central Bloom logo
Interaction: Hover reveals faction details, click to select
Animation: Smooth transitions between faction states
Responsive: Stack vertically on mobile, maintain aspect ratios

Interactive Elements:
├── Faction Emblem (SVG with hover animations)
├── Faction Name (Typography with custom font stacks)
├── Philosophy Quote (Rotating text carousel)
├── Color Palette Preview (Animated color bars)
├── Territory Map Fragment (Tactical overlay graphics)
└── "Choose This Faction" CTA (Faction-colored buttons)
```

#### **Technical Implementation**
```javascript
// Example faction data structure
const factionData = {
  directorate: {
    name: "Sky Bastion Directorate",
    philosophy: "Order from Chaos",
    colors: ["#161A1D", "#2E4053", "#85929E"],
    emblem: "/assets/factions/emblems/directorate.svg",
    territory: "/assets/territories/sky-bastion-preview.png",
    advantages: ["Disciplined Logistics", "Standard Equipment", "Long-range Coordination"],
    playstyle: "Structured tactical advancement with reliable equipment"
  }
  // ... additional factions
}

// State management for faction selection
const [selectedFaction, setSelectedFaction] = useState(null);
const [hoveredFaction, setHoveredFaction] = useState(null);
```

### Territorial Control Visualization

#### **WebSocket Integration**
```
WebSocket Server: ws://127.0.0.1:8765 (Terminal Grounds territorial system)
Connection: Real-time updates from territorial database
Data Format: JSON faction control updates every 30 seconds
Fallback: Static territorial map if WebSocket unavailable

Implementation Requirements:
├── Connection Management (auto-reconnect, error handling)
├── Data Parsing (territorial control percentages)
├── Visual Updates (animated faction territory changes)
├── Performance Optimization (throttled updates, canvas rendering)
└── Mobile Adaptation (simplified view for small screens)
```

#### **Territorial Map Interface**
```html
<div class="territorial-map">
  <canvas id="territory-canvas" width="1920" height="1080"></canvas>
  <div class="territorial-legend">
    <!-- Faction control percentages -->
    <div class="faction-control" v-for="faction in territorialData">
      <span class="faction-emblem" :style="factionColors[faction.id]"></span>
      <span class="faction-name">{{ faction.displayName }}</span>
      <span class="control-percentage">{{ faction.controlPercentage }}%</span>
    </div>
  </div>
</div>
```

### Pre-Registration System

#### **Multi-Step Registration Flow**
```
Step 1: Faction Selection (visual faction picker)
├── Required: Choose primary faction
├── Optional: Secondary faction preference
└── Progression: Unlocks faction-specific content

Step 2: Combat Role Preference
├── Options: Assault, Support, Reconnaissance, Heavy
├── Visual: Role icons with gameplay descriptions
└── Data: Informs alpha/beta invitation priority

Step 3: Experience Level
├── New to Extraction Shooters
├── Extraction Veteran (Tarkov, Hunt, etc.)
├── Tactical Shooter Enthusiast
└── Purpose: Matchmaking and onboarding customization

Step 4: Contact Information
├── Required: Email address
├── Optional: Discord username, Steam ID
├── Privacy: Clear GDPR compliance
└── Confirmation: Faction-themed welcome email
```

#### **Registration Database Schema**
```sql
CREATE TABLE pre_registrations (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  primary_faction VARCHAR(50) NOT NULL,
  secondary_faction VARCHAR(50),
  preferred_role VARCHAR(50),
  experience_level VARCHAR(50),
  discord_username VARCHAR(100),
  steam_id VARCHAR(100),
  registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  email_verified BOOLEAN DEFAULT FALSE,
  marketing_consent BOOLEAN DEFAULT FALSE
);

-- Faction preference tracking
CREATE TABLE faction_preferences (
  faction_name VARCHAR(50) PRIMARY KEY,
  registration_count INTEGER DEFAULT 0,
  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Community Integration Features

#### **Faction Warfare Dashboard**
```
Real-time Elements:
├── Active player count by faction
├── Current territorial control percentages  
├── Recent major territorial changes
├── Upcoming "Splice Events" (timed server events)
└── Community-generated faction content (Reddit/Discord feeds)

Static Elements:
├── Faction leaderboards (when available)
├── Developer faction insights
├── Community faction artwork galleries
└── Faction strategy guides and tactics
```

---

## Site Architecture

### Complete Sitemap

```
bloom.slurpgg.net/
├── / (Home)
│   ├── Hero Section (game overview, faction preview)
│   ├── Core Features (extraction mechanics, territorial warfare)
│   ├── Faction Showcase (interactive faction grid)
│   ├── Visual Gallery (concept art carousel)
│   ├── Pre-Registration CTA
│   └── Community Links
│
├── /factions/
│   ├── index (faction overview with territorial map)
│   ├── /directorate (Sky Bastion Directorate)
│   ├── /iron-scavengers (Iron Scavengers)
│   ├── /seventy-seven (The Seventy-Seven)
│   ├── /corporate (Corporate Hegemony)
│   ├── /nomads (Nomad Clans)  
│   ├── /archive (Archive Keepers)
│   └── /wardens (Civic Wardens)
│
├── /gameplay/
│   ├── index (gameplay overview)
│   ├── /extraction (extraction mechanics explained)
│   ├── /territorial-warfare (faction conflict systems)
│   ├── /technology-tiers (Field/Splice/Monolith progression)
│   ├── /weapons (weapon systems and customization)
│   └── /vehicles (faction vehicle specializations)
│
├── /world/
│   ├── index (post-Cascade world overview)
│   ├── /lore (comprehensive world background)
│   ├── /regions (IEZ zones and faction territories)  
│   ├── /timeline (events leading to current conflict)
│   └── /technology (Harvester tech and human adaptation)
│
├── /media/
│   ├── index (media gallery)
│   ├── /concept-art (environmental and faction art)
│   ├── /screenshots (gameplay screenshots when available)
│   ├── /videos (trailers and developer content)
│   └── /wallpapers (downloadable faction wallpapers)
│
├── /community/
│   ├── index (community hub)
│   ├── /discord (Discord server integration)
│   ├── /reddit (subreddit links and feeds)
│   ├── /fan-art (community artwork showcase)
│   └── /tournaments (competitive events when available)
│
├── /news/ (development blog)
│   ├── index (latest development updates)
│   ├── /development (technical development posts)
│   ├── /faction-spotlight (deep faction content)
│   └── /community-highlights (player features)
│
└── /legal/
    ├── /privacy (privacy policy)
    ├── /terms (terms of service)
    ├── /cookies (cookie policy)
    └── /eula (end user license agreement)
```

### Navigation Structure

#### **Primary Navigation**
```html
<nav class="primary-navigation">
  <ul>
    <li><a href="/">Home</a></li>
    <li class="has-dropdown">
      <a href="/factions/">Factions</a>
      <ul class="dropdown">
        <li><a href="/factions/directorate">Sky Bastion Directorate</a></li>
        <li><a href="/factions/iron-scavengers">Iron Scavengers</a></li>
        <li><a href="/factions/seventy-seven">The Seventy-Seven</a></li>
        <li><a href="/factions/corporate">Corporate Hegemony</a></li>
        <li><a href="/factions/nomads">Nomad Clans</a></li>
        <li><a href="/factions/archive">Archive Keepers</a></li>
        <li><a href="/factions/wardens">Civic Wardens</a></li>
      </ul>
    </li>
    <li><a href="/gameplay/">Gameplay</a></li>
    <li><a href="/world/">World</a></li>
    <li><a href="/media/">Media</a></li>
    <li><a href="/news/">News</a></li>
  </ul>
  <div class="navigation-cta">
    <a href="/register" class="btn-primary">Join the War</a>
  </div>
</nav>
```

#### **Mobile Navigation**
```
Hamburger Menu Structure:
├── Home
├── Factions (expandable section)
├── Gameplay  
├── World
├── Media
├── News
├── Community
└── Pre-Register (prominent CTA)

Mobile-Specific Features:
├── Swipe gestures for faction browsing
├── Collapsible sections for complex navigation
├── Sticky registration CTA
└── One-thumb navigation optimization
```

### URL Structure Standards
```
SEO-Optimized URL Patterns:
├── /factions/[faction-slug]/ (e.g., /factions/iron-scavengers/)
├── /gameplay/[system-slug]/ (e.g., /gameplay/extraction/)
├── /world/[lore-section]/ (e.g., /world/timeline/)
├── /news/[post-slug]/ (e.g., /news/faction-spotlight-directorate/)
└── /media/[category]/ (e.g., /media/concept-art/)

Canonical URL Requirements:
├── Trailing slashes for consistency
├── Lowercase with hyphens (not underscores)  
├── Descriptive slugs that match page content
└── 301 redirects for any URL changes
```

---

## Implementation Timeline

### Phase 1: Foundation (Weeks 1-2)
**Deliverables**: Basic site structure with core functionality

**Week 1: Setup & Architecture**
- [x] Project setup with chosen tech stack
- [x] Asset optimization pipeline implementation  
- [x] Responsive design system creation
- [x] Basic navigation and routing structure
- [ ] Performance monitoring integration

**Week 2: Core Pages**
- [ ] Homepage hero section with faction preview
- [ ] Basic faction pages with static content
- [ ] Gameplay overview page
- [ ] Asset integration testing and optimization

**Quality Gates**: 
- Mobile-first responsive design verified
- Core Web Vitals benchmarks established  
- Cross-browser testing completed
- Accessibility audit passed

### Phase 2: Interactive Features (Weeks 3-4) 
**Deliverables**: Faction system and pre-registration functionality

**Week 3: Faction System**
- [ ] Interactive faction selection interface
- [ ] Faction detail pages with complete lore integration
- [ ] Faction color theming system implementation
- [ ] Concept art galleries with lightbox functionality

**Week 4: Registration System**
- [ ] Multi-step pre-registration flow
- [ ] Database integration for user preferences
- [ ] Email confirmation system
- [ ] Faction preference analytics dashboard

**Quality Gates**:
- Faction selection system user testing
- Registration conversion rate optimization
- Email deliverability testing
- GDPR compliance verification

### Phase 3: Advanced Features (Weeks 5-6)
**Deliverables**: Real-time features and content management

**Week 5: Real-time Integration**  
- [ ] WebSocket connection to territorial system
- [ ] Live territorial control visualization
- [ ] Community integration (Discord, Reddit feeds)
- [ ] Performance optimization for real-time features

**Week 6: Content & Polish**
- [ ] Complete lore integration across all pages
- [ ] Advanced concept art galleries
- [ ] News/blog system implementation  
- [ ] SEO optimization and meta tag implementation

**Quality Gates**:
- WebSocket stability testing (24-hour uptime test)
- Performance testing with real-time features
- Content strategy validation
- SEO audit and optimization

### Phase 4: Launch Preparation (Weeks 7-8)
**Deliverables**: Production-ready website with monitoring

**Week 7: Testing & Optimization**
- [ ] Comprehensive cross-device testing
- [ ] Load testing and performance optimization
- [ ] Security audit and penetration testing
- [ ] Analytics and monitoring system integration

**Week 8: Launch & Monitoring**
- [ ] Soft launch with limited audience
- [ ] Performance monitoring and optimization
- [ ] Community feedback integration
- [ ] Final launch preparation

**Quality Gates**:
- Load testing (1000 concurrent users minimum)
- Security audit passed
- Launch readiness checklist completed
- Monitoring and alerting systems operational

### Ongoing Maintenance (Post-Launch)
**Deliverables**: Continuous improvement and content updates

**Monthly Deliverables**:
- [ ] Performance optimization based on real user data
- [ ] New faction content integration
- [ ] Community feature enhancements
- [ ] SEO content creation and optimization

**Quarterly Reviews**:
- [ ] Conversion funnel optimization
- [ ] User experience research and improvements  
- [ ] Technology stack updates and security patches
- [ ] Feature roadmap planning and prioritization

---

## Brand Guidelines

### Bloom Visual Identity System

#### **Core Brand Attributes**
- **Grounded Militarism**: Authentic tactical enhancement without fantasy excess
- **Technological Stratification**: Clear visual hierarchy from Field to Monolith grade
- **Environmental Scarring**: Post-cascade world shows its wounds
- **Extraction Tension**: High-stakes atmosphere with countdown urgency

#### **Typography Standards**
```css
/* Primary Typography Stack */
--font-primary: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
--font-display: "Rajdhani", "Orbitron", monospace; /* For headings and faction names */
--font-mono: "JetBrains Mono", "Fira Code", Consolas, monospace; /* For technical content */

/* Typography Scale */
--text-xs: 0.75rem;    /* 12px - Fine print, captions */
--text-sm: 0.875rem;   /* 14px - Body text small, metadata */  
--text-base: 1rem;     /* 16px - Primary body text */
--text-lg: 1.125rem;   /* 18px - Large body text */
--text-xl: 1.25rem;    /* 20px - Small headings */
--text-2xl: 1.5rem;    /* 24px - Section headings */
--text-3xl: 1.875rem;  /* 30px - Page headings */
--text-4xl: 2.25rem;   /* 36px - Display headings */
--text-5xl: 3rem;      /* 48px - Hero headings */

/* Font Weights */
--font-light: 300;
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
--font-black: 900;    /* For faction names and strong emphasis */
```

#### **Color System Standards**
```css
/* Core Brand Colors */
--bloom-primary: #0A0E14;      /* Deep space blue */
--bloom-secondary: #1A365D;    /* Cascade blue */ 
--bloom-accent: #00B4D8;       /* Alien tech cyan */
--bloom-warning: #F56500;      /* Danger orange */
--bloom-success: #38A169;      /* Mission success green */

/* Neutral Palette */
--neutral-50: #F7FAFC;
--neutral-100: #EDF2F7;
--neutral-200: #E2E8F0;
--neutral-300: #CBD5E0;
--neutral-400: #A0AEC0;
--neutral-500: #718096;
--neutral-600: #4A5568;
--neutral-700: #2D3748;
--neutral-800: #1A202C;
--neutral-900: #171923;

/* Faction Brand Colors (from faction data) */
[Data already provided in Asset Implementation section]

/* Usage Guidelines */
.primary-cta {
  background: linear-gradient(135deg, var(--bloom-accent), var(--bloom-secondary));
  color: var(--neutral-50);
}

.faction-themed {
  /* Dynamic faction coloring based on user selection */
  background: var(--faction-primary);
  border-color: var(--faction-secondary);
}
```

#### **Logo Usage Standards**
```
Primary Logo Applications:
├── Homepage Hero: Main logo, maximum impact sizing
├── Navigation Header: Horizontal logo, consistent placement
├── Email Signatures: Wordmark version preferred
├── Social Media: Emblem version for profile images
└── Favicon: Icon version optimized for 16px, 32px, 48px

Minimum Clear Space: 
├── Main Logo: 0.5x logo height on all sides
├── Horizontal Logo: 0.25x logo height on all sides
├── Icon Version: 0.125x icon width on all sides

Prohibited Usage:
├── Do not stretch or distort logo proportions
├── Do not place on backgrounds with insufficient contrast
├── Do not use logo smaller than 24px height
├── Do not modify colors without brand approval
└── Do not add effects, shadows, or borders
```

### Faction Visual Identity Standards

#### **Emblem Usage Guidelines**
```css
/* Faction Emblem Display Standards */
.faction-emblem {
  /* Base sizing for consistent visual hierarchy */
  --emblem-xs: 24px;    /* Navigation, breadcrumbs */
  --emblem-sm: 48px;    /* Inline content, lists */
  --emblem-md: 96px;    /* Card headers, profile images */
  --emblem-lg: 192px;   /* Section headers, feature cards */
  --emblem-xl: 384px;   /* Hero sections, full-page headers */
}

/* Responsive emblem sizing */
@media (max-width: 768px) {
  .faction-emblem {
    --emblem-lg: 144px;
    --emblem-xl: 288px;
  }
}
```

#### **Faction Content Theming**
```css
/* Dynamic faction theming system */
.faction-content {
  --faction-gradient: linear-gradient(
    135deg, 
    var(--faction-primary), 
    var(--faction-secondary)
  );
  
  background: var(--faction-gradient);
  border-left: 4px solid var(--faction-accent);
}

.faction-button {
  background: var(--faction-primary);
  color: var(--neutral-50);
  border: 2px solid var(--faction-secondary);
}

.faction-button:hover {
  background: var(--faction-secondary);
  border-color: var(--faction-accent);
}
```

#### **Environmental Storytelling Guidelines**
Each faction page should include:
- **Territory Aesthetic**: Visual themes matching faction domains
- **Technology Integration**: Equipment reflecting faction tech preferences  
- **Color Psychology**: Faction colors reinforcing narrative themes
- **Typography Choices**: Font selections supporting faction personality

---

## Quality Assurance Requirements

### Performance Testing Standards

#### **Core Web Vitals Targets**
```
Largest Contentful Paint (LCP): < 2.5 seconds
├── Hero images optimized for each breakpoint
├── Critical CSS inlined for above-fold content
├── WebP images with JPEG fallbacks
└── CDN delivery for all static assets

First Input Delay (FID): < 100 milliseconds  
├── JavaScript code splitting and lazy loading
├── Event listener optimization
├── Third-party script auditing
└── Performance budget enforcement

Cumulative Layout Shift (CLS): < 0.1
├── Fixed dimensions for all images and videos
├── Web font loading optimization
├── Dynamic content loading patterns
└── Skeleton loading states
```

#### **Load Testing Requirements**
```
Concurrent User Testing:
├── 100 concurrent users (minimum baseline)
├── 500 concurrent users (expected peak)
├── 1000 concurrent users (worst-case scenario)
└── WebSocket connection stability under load

Response Time Requirements:
├── Static pages: < 1.5 seconds global average
├── Dynamic content: < 3 seconds global average  
├── API endpoints: < 500ms average response time
└── WebSocket updates: < 100ms latency

Error Rate Thresholds:
├── HTTP errors: < 0.1% of total requests
├── JavaScript errors: < 0.01% of page loads
├── WebSocket disconnections: < 1% of connections
└── Form submission failures: < 0.1% of attempts
```

### Browser Compatibility Testing

#### **Testing Matrix**
```
Primary Browsers (Must Pass):
├── Chrome 90+ (Windows, macOS, Android)
├── Firefox 88+ (Windows, macOS)  
├── Safari 14+ (macOS, iOS)
├── Edge 90+ (Windows)
└── Samsung Internet 13+ (Android)

Secondary Browsers (Should Work):
├── Chrome 80+ (older versions)
├── Firefox 80+ (older versions)
├── Safari 13+ (older iOS devices)
└── Opera 75+ (desktop)

Legacy Support (Basic Functionality):
├── Internet Explorer 11 (functional graceful degradation)
├── Safari 12+ (basic feature support)
└── Chrome 70+ (limited animation support)
```

#### **Device Testing Requirements**
```
Mobile Devices (Primary):
├── iPhone 12/13/14 (Safari, Chrome)
├── Samsung Galaxy S21/S22 (Chrome, Samsung Internet)
├── Google Pixel 5/6 (Chrome)
└── iPad (Safari, Chrome)

Desktop Resolutions (Primary):
├── 1920x1080 (Full HD standard)
├── 1366x768 (Common laptop resolution)
├── 2560x1440 (QHD displays)  
└── 3840x2160 (4K displays)

Tablet Testing:
├── iPad Pro 12.9" (1024x1366)
├── Surface Pro (2880x1920)
└── Android tablets 10"+ (various resolutions)
```

### Accessibility Compliance

#### **WCAG 2.1 AA Requirements**
```
Perceivable Content:
├── Alt text for all images, including faction emblems
├── Color contrast ratio minimum 4.5:1 for normal text
├── Color contrast ratio minimum 3:1 for large text
├── No information conveyed by color alone
└── Captions for all video content

Operable Interface:
├── Full keyboard navigation support
├── Focus indicators visible and clear
├── No content flashing more than 3 times per second
├── Skip links for main navigation
└── Reasonable time limits with user control

Understandable Information:
├── Page language declared in HTML
├── Form labels clearly associated with inputs
├── Error messages specific and helpful
├── Navigation consistent across pages
└── Content organized with proper heading structure

Robust Implementation:
├── Valid HTML markup
├── ARIA labels for dynamic content
├── Screen reader compatibility testing
└── Progressive enhancement approach
```

#### **Accessibility Testing Tools**
```
Automated Testing:
├── axe-core integration in development
├── WAVE browser extension validation
├── Lighthouse accessibility audit
└── Color contrast analyzer verification

Manual Testing:
├── Keyboard-only navigation testing
├── Screen reader testing (NVDA, JAWS, VoiceOver)
├── High contrast mode verification
└── Magnification tool compatibility (200%+ zoom)
```

### Security Requirements

#### **Frontend Security Standards**
```
Content Security Policy (CSP):
├── Strict CSP headers for XSS prevention  
├── Whitelist approach for script sources
├── No inline JavaScript or CSS (development phase)
└── Regular CSP violation monitoring

Data Protection:
├── HTTPS enforcement across all pages
├── Secure cookie configuration  
├── No sensitive data in localStorage
└── Form data encryption for registration

Third-party Integration Security:
├── Subresource Integrity (SRI) for CDN assets
├── Regular security audits of dependencies
├── API key management best practices
└── Discord/social integration security review
```

#### **Privacy Compliance**
```
GDPR Compliance Requirements:
├── Clear cookie consent management
├── Privacy policy legal review and approval
├── User data deletion procedures
├── Data processing transparency documentation
└── Regular privacy impact assessments

User Consent Management:
├── Granular consent options for different data uses
├── Easy consent withdrawal mechanisms
├── Consent logging and audit trails
└── Child protection measures (age verification)
```

---

## Success Metrics

### Primary KPIs (Key Performance Indicators)

#### **Conversion Metrics**
```
Pre-Registration Conversion Rate:
├── Target: 5-8% of unique visitors register
├── Measurement: Registrations / Unique Visitors × 100
├── Baseline: Establish within first 30 days
└── Optimization: A/B testing on CTA placement and copy

Faction Selection Distribution:
├── Target: Relatively balanced faction interest
├── Measurement: Registration count per faction
├── Analysis: Weekly faction preference trends  
└── Application: Community balance and marketing focus

Email Engagement Rates:
├── Open Rate Target: 35-45%
├── Click-through Rate Target: 8-12%
├── Unsubscribe Rate Target: < 2%
└── Measurement: Weekly cohort analysis
```

#### **Engagement Metrics**
```
Session Duration:
├── Target: 4+ minutes average session
├── Measurement: GA4 average session duration
├── Segments: New vs returning visitors
└── Optimization: Content depth and navigation flow

Page Depth:
├── Target: 3.5+ pages per session
├── Measurement: Pages per session (GA4)
├── Analysis: Most common user journeys
└── Improvement: Internal linking and related content

Bounce Rate:
├── Target: < 45% overall bounce rate
├── Measurement: Single-page sessions
├── Segments: Traffic source analysis
└── Optimization: Landing page relevance and speed
```

#### **Technical Performance Metrics**
```
Core Web Vitals:
├── LCP Target: < 2.5s for 75% of users
├── FID Target: < 100ms for 75% of users
├── CLS Target: < 0.1 for 75% of users
└── Measurement: Real User Metrics (RUM) via Web Vitals API

Page Load Speed:
├── First Contentful Paint: < 1.5s
├── Time to Interactive: < 3.5s
├── Speed Index: < 2.5s
└── Measurement: Lighthouse CI integration

Error Rates:
├── JavaScript Errors: < 0.1% of pageviews
├── HTTP 4xx/5xx Errors: < 0.5% of requests  
├── WebSocket Connection Failures: < 2%
└── Form Submission Errors: < 1%
```

### Secondary KPIs (Supporting Metrics)

#### **Community Engagement**
```
Social Media Integration:
├── Discord Server Joins: Track referrals from website
├── Reddit Community Growth: Monitor subreddit subscriber growth
├── Social Sharing: Track faction content shares
└── Community Content: User-generated faction artwork submissions

Content Consumption:
├── Faction Page Views: Which factions generate most interest
├── Lore Section Engagement: Time spent on world-building content
├── Media Gallery Usage: Concept art download rates
└── News/Blog Readership: Development update engagement
```

#### **User Experience Metrics**
```
Accessibility Compliance:
├── Keyboard Navigation Success Rate: User testing sessions
├── Screen Reader Compatibility: Assistive technology testing
├── Color Contrast Compliance: Automated monitoring
└── Mobile Usability: Google Search Console mobile reports

Search Performance:
├── Organic Search Traffic Growth: Month-over-month growth
├── Keyword Ranking Improvements: Target faction and gameplay terms
├── Click-through Rate from Search: SERP CTR optimization
└── Local/Regional SEO: Geographic traffic distribution
```

### Analytics Implementation

#### **Google Analytics 4 Setup**
```javascript
// Enhanced E-commerce for Registration Tracking
gtag('event', 'faction_selected', {
  'custom_parameters': {
    'faction_name': selectedFaction,
    'user_experience_level': experienceLevel,
    'traffic_source': trafficSource
  }
});

gtag('event', 'registration_completed', {
  'custom_parameters': {
    'primary_faction': primaryFaction,
    'secondary_faction': secondaryFaction,
    'completion_time': registrationDuration
  }
});

// Custom Dimensions Configuration
// CD1: Faction Preference (Primary)
// CD2: Faction Preference (Secondary)  
// CD3: User Experience Level
// CD4: Traffic Source Category
// CD5: Device Category (Enhanced)
```

#### **Performance Monitoring Stack**
```
Real User Monitoring (RUM):
├── Core Web Vitals API integration
├── Custom performance mark measurements
├── Error tracking and reporting
└── User experience correlation analysis

Synthetic Monitoring:
├── Lighthouse CI for build-time performance testing
├── Uptime monitoring for critical pages
├── WebSocket connection health monitoring  
└── Cross-device performance benchmarking

A/B Testing Framework:
├── Faction selection interface variations
├── Hero section messaging optimization
├── Registration flow improvements
└── Mobile vs desktop experience optimization
```

### Reporting and Optimization Cycle

#### **Weekly Reports**
```
Performance Dashboard:
├── Core Web Vitals trends and alerts
├── Conversion funnel analysis
├── Top-performing content identification
└── Technical error rate monitoring

Marketing Effectiveness:
├── Traffic source performance comparison
├── Faction preference trends and analysis
├── Social media referral tracking
└── Email campaign performance metrics
```

#### **Monthly Deep Dives**
```
User Experience Analysis:
├── Heatmap analysis of faction selection interactions
├── User journey mapping and drop-off points
├── Mobile vs desktop behavior comparison  
├── Accessibility compliance audit
└── Performance optimization recommendations

Content Performance Review:
├── Page-level engagement analysis
├── Content gap identification
├── SEO keyword performance review
└── Community content integration opportunities
```

#### **Quarterly Strategic Reviews**
```
Business Impact Assessment:
├── Registration quality and engagement correlation
├── Community growth and retention analysis
├── Brand awareness and recognition tracking
└── Competitive landscape analysis

Technical Roadmap Planning:
├── Performance optimization prioritization
├── New feature implementation planning
├── Security audit and update requirements
└── Technology stack evolution considerations
```

---

## Conclusion

This comprehensive development brief provides external website teams with all necessary specifications to build a production-ready Terminal Grounds website. The document emphasizes the game's unique value propositions—grounded tactical gameplay, faction-driven conflict, and technological stratification—while providing concrete implementation guidance.

Key success factors include:

1. **Asset Integration**: Leveraging Terminal Grounds' extensive professional asset library
2. **Performance Excellence**: Achieving Core Web Vitals targets across all devices
3. **Faction System**: Creating compelling faction identity and selection experiences
4. **Community Building**: Fostering pre-launch engagement and faction loyalty
5. **Technical Innovation**: Implementing real-time territorial visualization

The timeline supports a structured 8-week development cycle with clear quality gates and success metrics. Post-launch success depends on continuous optimization based on real user data and community feedback.

**Next Steps for Implementation Teams**:
1. Confirm technical stack alignment with project requirements
2. Establish development environment and asset optimization pipeline  
3. Begin Phase 1 implementation with mobile-first responsive foundation
4. Schedule weekly progress reviews against outlined timeline and metrics

**Contact Information**:
- Technical Questions: Reference Terminal Grounds project documentation
- Asset Access: Use provided file paths and optimization guidelines
- Strategic Clarification: Refer to faction data and lore bible specifications

This brief serves as the definitive implementation guide for creating bloom.slurpgg.net as a premier extraction shooter website that converts visitors into engaged community members and pre-registered players.

---

**Document Control**:
- Version: 1.0
- Created: August 29, 2025
- Last Modified: August 29, 2025  
- Next Review: September 5, 2025
- Owner: Terminal Grounds Website Prompt Specialist
- Approved For Implementation: Yes