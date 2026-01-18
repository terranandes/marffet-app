---
trigger: always_on
---

## Location of formal product-releted document: ./product or ./
[SPEC] owns SPEC related
- ./product/specification.md
- ./product/backup_restore.md
- ./product/crawler_architecture.md
- ./product/data_pipeline.md

[PM] owns datasheet or README
- ./product/datasheet.md
- ./product/README.md, audiences are end-users who use the APP (not ME/Terran/BOSS/Agents)
- ./README.md, audiences are users who watch project or repository, located at GitHub

[PL][CODE][UI] Please owns software-perpsective document
- ./product/software_stack.md

[GCV] Please owns formal test plans, including automated browser flow using MCP lile Chrome DevTools/Playwright
- ./product/test_plan.md

## [PL] owns the meeting notes
- Format : /meeting/meeting_notes_$year_$month_$date_$version.md

## [CV] owns the files for product-level debugging/testing/verification
- ./tests/*
