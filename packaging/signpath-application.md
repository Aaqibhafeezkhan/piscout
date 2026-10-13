# SignPath Foundation application: answers for each form field

Apply at https://signpath.org/ (Foundation program, free for open-source projects).
The applicant creates the account and submits the form. Personal fields (name, email, company)
are intentionally not stored in this repository.

| Form field | Answer |
|---|---|
| **Project Name** | piscout |
| **Repository URL** | https://github.com/MilkteaTW1/piscout |
| **Homepage URL** | https://github.com/MilkteaTW1/piscout |
| **Download URL** | https://github.com/MilkteaTW1/piscout/releases (this page must mention SignPath once approved; see "After approval" below) |
| **Privacy Policy URL** | https://github.com/MilkteaTW1/piscout/blob/main/docs/PRIVACY.md |
| **Wikipedia URL** | leave empty (none exists) |
| **Tagline** | Find, connect to and manage Raspberry Pis on your network from Windows. |
| **Category** | The closest of: Networking / System utilities / Developer tools |
| **Description** | piscout is an open-source Windows desktop application for people who run Raspberry Pi computers. It discovers Raspberry Pis on the local network, provides a built-in SSH terminal and remote desktop in one window, shows an overview of several devices, and can write Raspberry Pi OS images to SD cards. It collects no data and stores saved logins only on the user's computer, encrypted with Windows DPAPI. |
| **Reputation** | Honest summary: this is a new project (first public release in October 2026) with no significant external adoption yet. Evidence of quality and transparency: MIT license; releases built only by GitHub Actions from tagged commits with automated tests (https://github.com/MilkteaTW1/piscout/actions); published SHA-256 for every release; a written privacy policy and known-risks documentation; a manifest submitted to the Windows Package Manager community repository (https://github.com/microsoft/winget-pkgs/pull/451835). |
| **Maintainer Type** | Individual / single maintainer |
| **Build System** | GitHub Actions |
| First / Last name, Email, Company | the applicant's own details |
| **Primary Discovery Channel** | answer truthfully with how you actually found SignPath (and the exact source in the optional field) |

## Be realistic
SignPath's open-source program prefers projects with an existing user base. A brand-new project may be
declined or asked to come back later. If that happens: keep releasing from CI, collect real usage
(stars, downloads, issues, winget installs), and re-apply.

## After approval
1. Add a sentence to the README download section, which SignPath requires:
   `Free code signing provided by [SignPath.io](https://signpath.io), certificate by [SignPath Foundation](https://signpath.org).`
2. Add the SignPath GitHub Action step to `.github/workflows/release.yml` before publishing the release.
3. Update the winget manifest hash for the signed `piscout.exe` (the file changes when it is signed).

## Facts reviewers usually check
| Item | Value |
|---|---|
| License | MIT (OSI approved) |
| Build | `.github/workflows/release.yml`, `windows-latest`, from the tagged commit |
| Artifact to sign | `piscout.exe` (PyInstaller one-file build) |
| Reproduce | `pip install -r requirements.txt pyinstaller`, then `build.bat` |
| Third-party code | xterm.js (MIT), noVNC (MPL-2.0), see `THIRD_PARTY_NOTICES.md` |
| Telemetry | none |
