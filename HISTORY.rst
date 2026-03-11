.. :changelog:

History
-------

For the complete changelog and detailed release information, see:
https://github.com/NOAA-PMEL/EcoFOCIpy/releases

This page provides a summary of major releases. For comprehensive information including
bug fixes, contributors, pull requests, and dependency updates, visit the GitHub releases page.

Latest Releases
---------------

0.2.5 (February 18, 2026) - February 2026 Release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Enhancements**:
- Enhanced nitrate plotting functions to support figure export
- Improved ERDDAP I/O functionality  
- Updated ISUS nitrate sensor parser
- Maintenance: Updated project dependencies

**Full Changelog**: https://github.com/NOAA-PMEL/EcoFOCIpy/compare/v0.2.4...v0.2.5

0.2.4 (August 8, 2025) - August 2025 Release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Major Features**:
- Enhanced ADCP processing and analysis tools
- **NEW**: Comprehensive ISUS (In Situ Ultraviolet Spectrophotometer) workflow support
  - Complete data parsing and processing
  - Configuration system updates

**⚠️ Breaking Changes**:
- MTR (Moored Time-series Recorder) update and refactor
- Legacy methods available in ``MTR_Parser.legacy`` for backwards compatibility

**Full Changelog**: https://github.com/NOAA-PMEL/EcoFOCIpy/compare/v0.2.3.1...v0.2.4

0.2.3.1 (July 11, 2025) - July 2025 Update - With Tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Improvements**:
- Expanded test coverage and improved test implementation
- Code quality improvements through pylinting
- Parser and processor refactoring:
  - ADCP processor improvements and cleanup
  - WET Labs sensor processor enhancements
  - WPAK (Wave PAcK) processor updates
  - Prooceanus parser refinements

**Full Changelog**: https://github.com/NOAA-PMEL/EcoFOCIpy/compare/v0.2.3...v0.2.3.1

0.2.3 (July 7, 2025) - Early July 2025 Update
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Features**:
- Enhanced SUNA (Submersible Ultraviolet Nitrate Analyzer) processing:
  - Delayed Q3 filtering implementation
  - Standardized plot styling
- Improved NetCDF export with float64 time encoding
- Added ``calculate_mean_offset`` to nitrate correction module
- SQL to GeoJSON conversion tools enhancements

**Full Changelog**: https://github.com/NOAA-PMEL/EcoFOCIpy/compare/v0.2.2...v0.2.3

0.2.2 (April 9, 2025) - April 2025 Release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Maintenance updates and dependency management
- Configuration improvements

**Full Changelog**: https://github.com/NOAA-PMEL/EcoFOCIpy/compare/v0.2.1...v0.2.2

0.2.1 (February 20, 2025) - February 2025 Release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Updates**:
- Web tools and GeoJSON conversion improvements
- Oxygen correction configuration updates
- Enhanced units handling and specifications
- Nitrate sensor parser improvements

**Full Changelog**: https://github.com/NOAA-PMEL/EcoFOCIpy/compare/v0.2.0...v0.2.1

0.2.0 (November 12, 2024) - November 2024 Major Release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**✨ Major New Feature**: Comprehensive SUNA Data Processing Package
- Complete SUNA sensor data processing workflow
- Quality control and validation utilities
- Enhanced plotting and visualization functions
- New contributor: @JiaxuZ

**Full Changelog**: https://github.com/NOAA-PMEL/EcoFOCIpy/compare/v0.1.9...v0.2.0

Historical Releases (0.1.x - 0.0.x)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See https://github.com/NOAA-PMEL/EcoFOCIpy/releases for complete release history.

**Notable milestones**:

- v0.1.9 (September 24, 2024) - Dependency updates
- v0.1.8 (September 13, 2024) - September 2024 release  
- v0.1.7 (March 21, 2024) - March 2024 release
- v0.1.6 (February 7, 2024) - February 2024 release
- v0.1.5 (November 15, 2023) - November 2023 release
- v0.1.4 (January 20, 2023) - January 2023 release
- v0.1.3 (October 24, 2022) - October 2022 release
- v0.1.2 (July 13, 2022) - July 2022 release with Anderaa corrections
- v0.1.1 (February 2, 2022) - Initial test implementation
- v0.1.0 (January 5, 2022) - Python 3.8+ requirement
- v0.0.7 (July 16, 2021) - ERDDAP methods added
- v0.0.6 (April 23, 2021) - **Unified NetCDF API** and ADCP support
  - Breaking change: unified NetCDF generation for moored/CTD data
- v0.0.5 (April 7, 2021) - SBE CTD processing
- v0.0.4 (April 5, 2021) - Requirements fix
- v0.0.3 (April 2, 2021) - WET Labs Eco parsers
- v0.0.2 (March 31, 2021) - SBE instruments support
- v0.0.1 (March 26, 2021) - **Super early pre-release**
  - WPAK processing (without metadata)
  - SBE39 partial support
  - Mooring YAML config builder

**For all releases and detailed information**, see:
https://github.com/NOAA-PMEL/EcoFOCIpy/releases

