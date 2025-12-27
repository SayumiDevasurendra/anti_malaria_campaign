# Stain Time Optimization Component

**Automated Optimal Giemsa Staining Time Determination via Slide Grading**

This component determines optimal staining times for 10% (rapid) and 3% (slow) Giemsa working solutions by automated grade-based analysis of minute-by-minute slide sweeps, aligned with AMC/WHO standards.

---

## Component Overview

### Capabilities
1. **Automated Slide Grading**: CNN-based grading of thin and thick blood smears (AMC Grades I-V)
2. **Optimal Time Selection**: Recommends earliest acceptable staining time per batch via minute-by-minute analysis
3. **Failure Diagnosis**: Provides SOP-aligned reason codes and corrective actions
4. **Pattern Aggregation**: Tracks optimal staining times across sites for national-level insights

### Technical Features
- AMC/WHO-aligned 5-grade classification (I-V)
- Pass/fail decision logic (Grade III threshold)
- Multi-architecture support (ResNet, EfficientNet, MobileNet)
- Conservative stain-aware augmentation
- Mixed precision training (AMP)
- Calibrated confidence scores

---

## Component Integration

This is one component of the larger AMC malaria detection system. Other team members will add their components:

- **Slide Quality Assessment** (macro image quality - separate component)
- **Parasite Detection** (separate component)
- **Stage Typing** (separate component)
- **Gametocyte Counting** (separate component)

**Naming Convention:** All files use "stain_time" or "StainTime" prefix to avoid conflicts.

---

## Documentation

Comprehensive documentation for model training and class imbalance handling:

- **[Quick Start Guide](docs/QUICK_START.md)** - Get started with balanced training in 3 steps
- **[Balanced Training Guide](docs/BALANCED_TRAINING_GUIDE.md)** - Complete guide for handling class imbalance
- **[Implementation Summary](docs/IMPLEMENTATION_SUMMARY.md)** - Overview of the balanced training implementation
- **[Architecture Overview](docs/ARCHITECTURE.md)** - Hybrid balancing architecture details

---

**Component:** Stain Time Optimization
**Author:** Sayumi Devasurendra
**Version:** 0.1.0
