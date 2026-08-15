import ast
from pathlib import Path
import unittest

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    PROJECT_ROOT
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)
INSTALLER_PATH = PROJECT_ROOT / "installer" / "SMWStreamTrackerInstaller.iss"
INSTALLER_BANNER_PATH = PROJECT_ROOT / "installer" / "smw_installer_banner.png"


class FirstLaunchSetupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = MODULE_PATH.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)
        cls.methods = {
            node.name: node
            for node in ast.walk(cls.tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }

    def test_first_launch_flag_and_welcome_schedule_are_present(self):
        self.assertIn('"first_launch_welcome_completed": False', self.source)
        self.assertIn(
            "self.root.after(1100, self._offer_first_launch_welcome)",
            self.source,
        )
        installer = INSTALLER_PATH.read_text(encoding="utf-8")
        self.assertIn('"first_launch_welcome_completed": false', installer)
        self.assertIn(
            '"first_launch_mister_setup_requested": False',
            self.source,
        )
        self.assertIn(
            '"first_launch_mister_setup_requested": ',
            installer,
        )

    def test_installer_offers_translated_mister_platform_and_setup(self):
        installer = INSTALLER_PATH.read_text(encoding="utf-8")
        for language in (
            "english",
            "australian",
            "spanish",
            "french",
            "german",
            "brazilianportuguese",
        ):
            for key in ("MiSTerOption", "MiSTerSetupOption", "ReadyMiSTer"):
                with self.subTest(language=language, key=key):
                    self.assertIn(f"{language}.{key}=", installer)

        self.assertIn(
            "PlatformPage.Add(ExpandConstant('{cm:MiSTerOption}'));",
            installer,
        )
        self.assertIn(
            "DependencyPage.Add(ExpandConstant('{cm:MiSTerSetupOption}'));",
            installer,
        )
        self.assertIn("function ShouldSetUpMiSTer: Boolean;", installer)
        self.assertIn("Result := 'MiSTer'", installer)

    def test_complete_installer_uses_the_shared_banner_and_blue_theme(self):
        installer = INSTALLER_PATH.read_text(encoding="utf-8")

        self.assertIn(
            "WizardStyle=modern dark polar includetitlebar hidebevels",
            installer,
        )
        self.assertIn("WizardBackColor=#19283F", installer)
        self.assertIn("WizardSizePercent=150", installer)
        self.assertIn("WizardImageFile=\n", installer)
        self.assertIn("WizardSmallImageFile=\n", installer)
        self.assertIn(
            'Source: "smw_installer_banner.png"; '
            "Flags: dontcopy noencryption",
            installer,
        )
        self.assertIn("procedure ConfigureInstallerTheme;", installer)
        self.assertIn("InstallerBanner.PngImage.LoadFromFile(BannerFile);", installer)
        self.assertIn("WizardForm.OuterNotebook.Top := ContentTop;", installer)
        self.assertIn(
            "WizardForm.WelcomeLabel1.Alignment := taCenter;",
            installer,
        )
        self.assertIn(
            "WizardForm.FinishedHeadingLabel.Alignment := taCenter;",
            installer,
        )
        self.assertIn("ConfigureInstallerTheme;", installer)

        with Image.open(INSTALLER_BANNER_PATH) as banner:
            self.assertEqual(banner.size, (1040, 292))
            self.assertEqual(banner.mode, "RGB")

    def test_installer_folder_page_explains_existing_folders_and_optional_obs(self):
        installer = INSTALLER_PATH.read_text(encoding="utf-8")

        localized_markers = {
            "english": (
                "Create new folders, or use folders you already have.",
                "OBS / stream text output (optional):",
            ),
            "australian": (
                "Create new folders, or use folders you already have, mate.",
                "OBS / stream text output (optional, mate):",
            ),
            "spanish": (
                "Cree carpetas nuevas o use las carpetas que ya tiene.",
                "Salida de texto para OBS / streaming (opcional):",
            ),
            "french": (
                "Créez de nouveaux dossiers ou utilisez les dossiers que vous possédez déjà.",
                "Sortie texte OBS / stream (facultative) :",
            ),
            "german": (
                "Erstellen Sie neue Ordner oder verwenden Sie bereits vorhandene Ordner.",
                "OBS-/Stream-Textausgabe (optional):",
            ),
            "brazilianportuguese": (
                "Crie novas pastas ou use as pastas que você já tem.",
                "Saída de texto do OBS / transmissão (opcional):",
            ),
        }
        for language, (folder_help, obs_label) in localized_markers.items():
            with self.subTest(language=language):
                self.assertIn(f"{language}.FolderSubtitle={folder_help}", installer)
                self.assertIn(f"{language}.OBSFolder={obs_label}", installer)

        for phrase in ("titles", "creators", "exits", "death counters"):
            self.assertIn(phrase, installer)
        for language in localized_markers:
            self.assertIn(f"{language}.OBSFolderNote=", installer)
        self.assertEqual(
            installer.count("FolderPage.Add(ExpandConstant('{cm:ROMLibrary}'));"),
            1,
        )
        self.assertNotIn(
            "FolderPage.Add(ExpandConstant('{cm:OBSFolder}'));",
            installer,
        )
        self.assertIn("FolderOBSEdit := TNewEdit.Create(FolderPage);", installer)
        self.assertIn("FolderOBSEdit.Parent := FolderPage.Surface;", installer)
        self.assertIn(
            "FolderOBSBrowseButton.OnClick := @BrowseForObsFolder;",
            installer,
        )
        self.assertIn("FolderOBSNote.Parent := FolderPage.Surface;", installer)
        self.assertIn("FolderOBSNote.WordWrap := True;", installer)
        self.assertNotIn("if CurPageID = FolderPage.ID then", installer)
        self.assertIn("if Trim(FolderOBSEdit.Text) <> '' then", installer)
        self.assertIn("JsonEscape(FolderOBSEdit.Text)", installer)
        self.assertNotIn("FolderPage.Values[1]", installer)

    def test_installer_uses_verified_fast_silent_retroarch_setup(self):
        installer = INSTALLER_PATH.read_text(encoding="utf-8")

        self.assertIn(
            'Source: "https://buildbot.libretro.com/stable/1.22.2/'
            'windows/x86_64/RetroArch-Win64-setup.exe";',
            installer,
        )
        self.assertIn(
            'Hash: "bb2b95329542d98d951bb381c0dd57e803d846242878895f12d374b87201c1c9";',
            installer,
        )
        self.assertIn("ExternalSize: 209037907", installer)
        self.assertIn(
            'DestDir: "{tmp}";',
            installer,
        )
        self.assertIn(
            "Flags: external download ignoreversion deleteafterinstall",
            installer,
        )
        self.assertNotIn('Verb: "runas"', installer)
        self.assertIn("procedure InstallPortableRetroArch;", installer)
        self.assertIn("if not ShellExec(", installer)
        self.assertIn("'runas',", installer)
        self.assertIn("    '/S',", installer)
        self.assertNotIn("'/S /D=' + InstallDirectory", installer)
        self.assertIn("ewWaitUntilTerminated", installer)
        self.assertIn("InstallPortableRetroArch;", installer)
        self.assertIn(
            "ExtractArchive(CoreArchivePath, CoreDirectory, '', True, nil);",
            installer,
        )

        portable_executable = "{sd}\\RetroArch-Win64\\retroarch.exe"
        portable_core = (
            "{sd}\\RetroArch-Win64\\cores\\"
            "bsnes_mercury_performance_libretro.dll"
        )
        self.assertIn(portable_executable, installer)
        self.assertIn(portable_core, installer)
        self.assertIn("function SelectedRetroArchExecutablePath: String;", installer)
        self.assertIn("JsonEscape(SelectedRetroArchExecutablePath)", installer)
        self.assertIn("procedure ConfigurePortableRetroArch;", installer)
        self.assertIn(
            "SetRetroArchSetting(Settings, 'network_cmd_enable', '\"true\"');",
            installer,
        )
        self.assertIn(
            "SetRetroArchSetting(Settings, 'network_cmd_port', '\"55355\"');",
            installer,
        )

        translated_portable_markers = {
            "english": "Install portable RetroArch",
            "australian": "Install portable RetroArch",
            "spanish": "Instalar RetroArch portátil",
            "french": "Installer RetroArch portable",
            "german": "Portables RetroArch",
            "brazilianportuguese": "Instalar RetroArch portátil",
        }
        for language, marker in translated_portable_markers.items():
            with self.subTest(language=language):
                self.assertIn(
                    f"{language}.RetroArchInstallOption={marker}",
                    installer,
                )

        clean_install_markers = {
            "english": "select if you only want a new/clean install",
            "australian": "fresh/clean install, mate",
            "spanish": "instalación nueva/limpia",
            "french": "nouvelle installation propre",
            "german": "neue/saubere Installation",
            "brazilianportuguese": "instalação nova/limpa",
        }
        self.assertNotIn("(no separate setup wizard)", installer)
        for language, marker in clean_install_markers.items():
            with self.subTest(clean_install_language=language):
                self.assertIn(
                    f"{language}.RetroArchInstallOption=",
                    installer,
                )
                self.assertIn(marker, installer)

        documentation_markers = {
            PROJECT_ROOT / "README.md": "No separate RetroArch setup wizard opens.",
            PROJECT_ROOT / "docs" / "README.en.txt": "No separate RetroArch setup wizard opens.",
            PROJECT_ROOT / "docs" / "README.au.txt": "No second white wizard, mate",
            PROJECT_ROOT / "docs" / "README.es.txt": "No se abre otro asistente",
            PROJECT_ROOT / "docs" / "README.fr.txt": "Aucun autre assistant",
            PROJECT_ROOT / "docs" / "README.de.txt": "Ein zweiter RetroArch-Assistent",
            PROJECT_ROOT / "docs" / "README.pt-BR.txt": "Nenhum outro assistente",
        }
        for path, marker in documentation_markers.items():
            with self.subTest(path=path.name):
                self.assertIn(marker, path.read_text(encoding="utf-8"))

    def test_uninstall_removes_tracker_state_but_preserves_tools_and_roms(self):
        installer = INSTALLER_PATH.read_text(encoding="utf-8")

        self.assertIn("[UninstallDelete]", installer)
        for state_path in (
            "SMWStreamTrackerConfig.json",
            "SMWStreamTrackerTimes.json",
            "SMWStreamTrackerDeaths.json",
            "SMWStreamTrackerLevelProgress.json",
            "SMWStreamTracker\\SMWStreamTracker.db",
            "SMWStreamTracker\\Backups",
            "SMWStreamTracker\\AutomaticBackups",
            "SMWStreamTracker\\Rollback",
            "SMWStreamTracker\\Updates",
            "SMWStreamTracker\\Logs",
            "SMWStreamTracker\\DependencyDownloads",
            "Tools\\LiveSplitGameTimer",
            "Tools\\LiveSplitLevelTimer",
            "UninstallObsOutputPath.txt",
        ):
            with self.subTest(state_path=state_path):
                self.assertIn(state_path, installer)

        for protected_tool in ("SNI", "QUsb2Snes"):
            with self.subTest(protected_tool=protected_tool):
                installed_tool_line = next(
                    line
                    for line in installer.splitlines()
                    if f'DestDir: "{{app}}\\Tools\\{protected_tool}"' in line
                )
                self.assertIn(protected_tool, installed_tool_line)
                tool_block_start = installer.index(installed_tool_line)
                tool_block_end = installer.find("\n\n", tool_block_start)
                tool_block = installer[tool_block_start:tool_block_end]
                self.assertIn("uninsneveruninstall", tool_block)

        # RetroArch's faster nested installer owns its files, so the tracker
        # uninstaller never registers or removes them.
        self.assertIn("procedure InstallPortableRetroArch;", installer)
        self.assertIn("{sd}\\RetroArch-Win64", installer)

        uninstall_section = installer.split("[UninstallDelete]", 1)[1].split(
            "[Icons]", 1
        )[0]
        for protected_name in ("SNI", "QUsb2Snes", "RetroArch"):
            self.assertNotIn(f"Tools\\{protected_name}", uninstall_section)
        self.assertNotIn("platform_rom_library_folder", uninstall_section)
        self.assertNotIn("rom_builder_library_folder", uninstall_section)
        self.assertNotIn("output_folder", uninstall_section)
        self.assertNotIn('Name: "{app}\\Tools"', uninstall_section)

        self.assertIn("UNINSTALL_OBS_PATH_FILE", self.source)
        self.assertIn("UninstallObsOutputPath.txt", self.source)
        self.assertIn(
            "procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);",
            installer,
        )
        self.assertIn("if CurUninstallStep = usUninstall then", installer)
        self.assertNotIn("function InitializeUninstall: Boolean;", installer)
        self.assertIn("procedure DeleteTrackerObsOutputFiles;", installer)
        for obs_filename in (
            "author.txt",
            "exits.txt",
            "level_deaths.txt",
            "death_counter.txt",
            "total_deaths.txt",
            "hack_name.txt",
            "level_timer.txt",
            "game_timer.txt",
            "SMWTracker.log",
        ):
            with self.subTest(obs_filename=obs_filename):
                self.assertIn(
                    "DeleteFile(AddBackslash(OutputFolder) + "
                    f"'{obs_filename}');",
                    installer,
                )
        self.assertNotIn("DelTree(OutputFolder", installer)

    def test_uninstall_reset_makes_the_welcome_splash_fresh_again(self):
        installer = INSTALLER_PATH.read_text(encoding="utf-8")
        uninstall_section = installer.split("[UninstallDelete]", 1)[1].split(
            "[Icons]", 1
        )[0]

        self.assertIn("SMWStreamTrackerConfig.json", uninstall_section)
        self.assertIn('"first_launch_welcome_completed": false', installer)
        self.assertIn('"first_launch_welcome_completed": False', self.source)
        self.assertIn(
            "self.root.after(1100, self._offer_first_launch_welcome)",
            self.source,
        )

    def test_complete_installer_allows_only_one_installed_copy(self):
        installer = INSTALLER_PATH.read_text(encoding="utf-8")

        self.assertIn("DisableDirPage=yes", installer)
        self.assertIn("UsePreviousAppDir=no", installer)
        self.assertIn(
            "function FindExistingTrackerInstallation(",
            installer,
        )
        self.assertIn(
            "function RemoveExistingTrackerInstallation: Boolean;",
            installer,
        )
        self.assertIn(
            "ExistingInstallActionPage := CreateInputOptionPage(",
            installer,
        )
        self.assertIn("ExistingInstallFreshOption", installer)
        self.assertIn("ExistingInstallRemoveOption", installer)
        self.assertIn(
            "ExistingInstallActionPage.SelectedValueIndex = 1",
            installer,
        )
        self.assertIn("WizardForm.Close;", installer)
        self.assertIn("DeleteTrackerOwnedState;", installer)
        self.assertIn("DeleteKnownTrackerApplicationFiles", installer)
        self.assertIn("RegDeleteKeyIncludingSubkeys", installer)

        for language in (
            "english",
            "australian",
            "spanish",
            "french",
            "german",
            "brazilianportuguese",
        ):
            for key in (
                "ExistingInstallActionTitle",
                "ExistingInstallActionSubtitle",
                "ExistingInstallActionDescription",
                "ExistingInstallFreshOption",
                "ExistingInstallRemoveOption",
                "ExistingInstallRemovalFailed",
                "ExistingInstallRemovalComplete",
            ):
                with self.subTest(language=language, key=key):
                    self.assertIn(f"{language}.{key}=", installer)

        cleanup_source = installer.split(
            "procedure DeleteKnownTrackerApplicationFiles", 1
        )[1].split("function RemoveExistingTrackerInstallation", 1)[0]
        self.assertNotIn("Tools\\RetroArch", cleanup_source)
        self.assertNotIn("Tools\\SNI", cleanup_source)
        self.assertNotIn("Tools\\QUsb2Snes", cleanup_source)
        self.assertNotIn("ROM", cleanup_source)

    def test_guided_setup_methods_are_present(self):
        expected = {
            "_offer_first_launch_welcome",
            "start_guided_app_setup",
            "_guided_downloads_menu_button_clicked",
            "_guided_setup_set_stage",
            "_guided_setup_target_menu_entries",
            "_guided_install_optional_software",
            "_guided_optional_software_completed",
            "_guided_setup_show_catalog_filter_prompt",
            "_guided_setup_catalog_refreshed",
            "_guided_setup_downloader_opened",
            "_guided_setup_show_fxpak_prompt",
            "_guided_setup_hacks_downloaded",
            "_prompt_guided_obs_setup",
            "open_guided_obs_text_setup",
            "open_livesplit_obs_setup_guide",
        }
        self.assertFalse(expected.difference(self.methods))

    def test_required_stage_handoffs_are_hooked(self):
        self.assertIn(
            "self._guided_optional_software_completed(software)",
            ast.get_source_segment(
                self.source,
                self.methods["_finish_optional_software_install"],
            ),
        )
        self.assertIn(
            "self._guided_setup_catalog_refreshed()",
            ast.get_source_segment(
                self.source,
                self.methods["_finish_catalog_refresh"],
            ),
        )
        download_finish_source = ast.get_source_segment(
            self.source,
            self.methods["_finish_filtered_hack_download"],
        )
        self.assertIn(
            'getattr(\n                self,\n                "_guided_setup_hacks_downloaded"',
            download_finish_source,
        )
        self.assertIn("if callable(guided_setup_complete):", download_finish_source)
        self.assertIn("guided_setup_complete()", download_finish_source)

    def test_guide_starts_at_downloads_and_hides_after_it_is_selected(self):
        start_source = ast.get_source_segment(
            self.source,
            self.methods["start_guided_app_setup"],
        )
        click_source = ast.get_source_segment(
            self.source,
            self.methods["_guided_downloads_menu_button_clicked"],
        )
        self.assertIn('self._guided_setup_set_stage("downloads")', start_source)
        self.assertIn('if stage == "downloads":', click_source)
        self.assertIn("self._guided_setup_hide_dialog()", click_source)
        self.assertIn('self._guided_setup_set_stage("connection")', click_source)
        self.assertIn('elif stage == "downloads_again":', click_source)
        self.assertIn(
            'self._guided_setup_set_stage("download_missing")',
            click_source,
        )

    def test_connection_step_flashes_parent_and_all_four_choices(self):
        targets_source = ast.get_source_segment(
            self.source,
            self.methods["_guided_setup_target_menu_entries"],
        )
        self.assertIn('if stage == "connection":', targets_source)
        self.assertIn("connection_setup_menu_index", targets_source)
        self.assertIn("connection_option_menu_indexes", targets_source)
        self.assertIn(
            "self.connection_option_menu_indexes = tuple(",
            self.source,
        )
        self.assertIn('"mister",', targets_source)
        self.assertIn(
            "self._guided_open_mister_setup,",
            self.source,
        )

    def test_posted_native_menu_entries_are_stable_and_clickable(self):
        tick_source = ast.get_source_segment(
            self.source,
            self.methods["_guided_setup_flash_tick"],
        )
        start_source = ast.get_source_segment(
            self.source,
            self.methods["_guided_setup_start_flash"],
        )
        self.assertNotIn("entryconfigure", tick_source)
        self.assertIn("menu.entryconfigure(", start_source)
        self.assertIn('label=f"\\u2605  {label}"', start_source)
        self.assertIn('foreground=THEME["yellow"]', start_source)

    def test_connection_routes_require_the_expected_installs(self):
        completion_source = ast.get_source_segment(
            self.source,
            self.methods["_guided_optional_software_completed"],
        )
        self.assertIn('if choice == "qusb2snes":', completion_source)
        self.assertIn('configured_file("qusb2snes_path"', completion_source)
        self.assertIn('elif choice == "sni_retroarch":', completion_source)
        self.assertIn('configured_file("sni_path"', completion_source)
        self.assertIn(
            'configured_file("retroarch_executable_path")',
            completion_source,
        )
        self.assertIn(
            'configured_file("retroarch_core_path")',
            completion_source,
        )
        self.assertIn('elif choice == "mister":', completion_source)
        self.assertIn('"mister_ssh_fingerprint"', completion_source)

    def test_installer_selected_mister_flashes_one_click_setup(self):
        start_source = ast.get_source_segment(
            self.source,
            self.methods["start_guided_app_setup"],
        )
        target_source = ast.get_source_segment(
            self.source,
            self.methods["_guided_setup_target_widget"],
        )
        mister_source = ast.get_source_segment(
            self.source,
            self.methods["open_mister_setup"],
        )
        self.assertIn("first_launch_mister_setup_requested", start_source)
        self.assertIn("mister_setup_automatic_button", target_source)
        self.assertIn(
            'self._guided_optional_software_completed("mister")',
            mister_source,
        )
        self.assertIn(
            "dialog.after_idle(self._guided_setup_refresh_connection_flash)",
            mister_source,
        )

    def test_mister_guide_copy_is_translated_in_every_language(self):
        self.assertEqual(self.source.count('"mister_connection_title":'), 6)
        self.assertEqual(self.source.count('"mister_connection_text":'), 6)

    def test_catalog_and_download_handoffs_follow_requested_order(self):
        catalog_source = ast.get_source_segment(
            self.source,
            self.methods["open_smwcentral_catalog_browser"],
        )
        refresh_source = ast.get_source_segment(
            self.source,
            self.methods["_guided_setup_catalog_refreshed"],
        )
        downloader_source = ast.get_source_segment(
            self.source,
            self.methods["_guided_setup_downloader_opened"],
        )
        self.assertIn('self._guided_setup_set_stage("refresh_catalog")', catalog_source)
        self.assertIn("_guided_setup_show_catalog_filter_prompt", catalog_source)
        self.assertIn('self._guided_setup_set_stage("downloads_again")', refresh_source)
        self.assertIn('self._guided_setup_set_stage("download_all")', downloader_source)
        self.assertIn("_guided_setup_show_fxpak_prompt", downloader_source)

    def test_fresh_install_can_open_catalog_before_the_first_refresh(self):
        open_source = ast.get_source_segment(
            self.source,
            self.methods["open_hack_downloader"],
        )
        preview_source = ast.get_source_segment(
            self.source,
            self.methods["_refresh_downloader_preview"],
        )
        game_library_source = ast.get_source_segment(
            self.source,
            self.methods["open_game_library"],
        )

        self.assertIn(
            "if not self.hack_catalog and not catalog_view_only:",
            open_source,
        )
        self.assertIn(
            "Your SMW Central catalog has not been downloaded yet.",
            open_source,
        )
        self.assertIn(
            "No SMW Central catalog has been downloaded yet.",
            preview_source,
        )
        self.assertIn(
            'text="Refresh Moderated Hacks from SMW Central"',
            open_source,
        )
        self.assertIn(
            "Your SMW Central catalog has not been downloaded yet.",
            game_library_source,
        )
        self.assertNotIn(
            "The tracker database catalog is still loading.",
            open_source,
        )

    def test_instruction_and_completion_popups_use_blue_app_dialogs(self):
        filter_source = ast.get_source_segment(
            self.source,
            self.methods["_guided_setup_show_catalog_filter_prompt"],
        )
        fxpak_source = ast.get_source_segment(
            self.source,
            self.methods["_guided_setup_show_fxpak_prompt"],
        )
        complete_source = ast.get_source_segment(
            self.source,
            self.methods["_prompt_guided_obs_setup"],
        )
        self.assertIn("self._show_localized_info(", filter_source)
        self.assertIn('"filter_prompt"', filter_source)
        self.assertIn("self._show_localized_info(", fxpak_source)
        self.assertIn('"fxpak_prompt"', fxpak_source)
        self.assertIn('bg=THEME["blue"]', complete_source)
        self.assertIn('"setup_complete_message"', complete_source)
        self.assertIn('"obs_prompt"', complete_source)

    def test_setup_complete_opens_blue_obs_feature_chooser(self):
        complete_source = ast.get_source_segment(
            self.source,
            self.methods["_prompt_guided_obs_setup"],
        )
        chooser_source = ast.get_source_segment(
            self.source,
            self.methods["open_guided_obs_setup_chooser"],
        )
        obs_text_source = ast.get_source_segment(
            self.source,
            self.methods["open_guided_obs_text_setup"],
        )
        livesplit_source = ast.get_source_segment(
            self.source,
            self.methods["open_livesplit_obs_setup_guide"],
        )

        self.assertIn("self.open_guided_obs_setup_chooser()", complete_source)
        self.assertIn('bg=THEME["blue"]', chooser_source)
        self.assertIn('"obs_text_files_button"', chooser_source)
        self.assertIn('"livesplit_obs_button"', chooser_source)
        self.assertIn('"livesplit_obs_button"', obs_text_source)
        self.assertIn('"obs_text_files_button"', livesplit_source)

    def test_obs_feature_chooser_copy_is_translated_in_every_language(self):
        for language_code in ("en", "au", "es", "fr", "de", "pt-BR"):
            with self.subTest(language_code=language_code):
                self.assertIn(
                    f'"{language_code}": {{',
                    self.source,
                )
        for key in (
            "obs_choice_title",
            "obs_choice_message",
            "obs_text_files_button",
            "livesplit_obs_button",
            "choose_obs_folder_button",
            "obs_folder_error",
        ):
            self.assertGreaterEqual(self.source.count(f'"{key}"'), 6)

    def test_download_actions_include_patch_wording(self):
        self.assertIn('"Download & Patch Missing Hacks…"', self.source)
        self.assertIn('"Download & Patch All Matching Hacks"', self.source)
        self.assertNotIn('"Download Missing Hacks…"', self.source)
        self.assertNotIn('"Download All Matching Hacks"', self.source)

    def test_setup_help_menu_and_obs_paths_are_available(self):
        self.assertIn('self._setup_guide_text("setup_menu")', self.source)
        self.assertIn('self._setup_guide_text("app_setup")', self.source)
        self.assertIn('self._setup_guide_text("obs_setup")', self.source)
        self.assertIn('self._setup_guide_text("livesplit_setup")', self.source)
        for filename in (
            "hack_name.txt",
            "author.txt",
            "exits.txt",
            "level_deaths.txt",
            "total_deaths.txt",
        ):
            with self.subTest(filename=filename):
                self.assertIn(f'"{filename}"', self.source)

    def test_obs_setup_explains_how_to_reuse_existing_text_sources(self):
        obs_source = ast.get_source_segment(
            self.source,
            self.methods["open_guided_obs_text_setup"],
        )
        self.assertIn('"obs_existing_source_note"', obs_source)
        self.assertIn('highlightbackground=THEME["yellow"]', obs_source)
        self.assertIn('"\\u2605  "', obs_source)
        self.assertIn("self._select_guided_obs_text_folder()", obs_source)
        self.assertIn('"choose_obs_folder_button"', obs_source)

    def test_livesplit_obs_guide_uses_two_copies_ports_and_window_capture(self):
        settings_source = ast.get_source_segment(
            self.source,
            self.methods["_open_settings_dialog"],
        )
        guide_source = ast.get_source_segment(
            self.source,
            self.methods["open_livesplit_obs_setup_guide"],
        )
        self.assertNotIn('"livesplit_obs_note"', settings_source)
        self.assertNotIn('"livesplit_obs_button"', settings_source)
        self.assertIn("local_game_port.get()", settings_source)
        self.assertIn("local_level_port.get()", settings_source)
        self.assertIn('"livesplit_obs_instructions"', guide_source)
        self.assertIn("game_port=resolved_game_port", guide_source)
        self.assertIn("level_port=resolved_level_port", guide_source)
        self.assertIn('style="Mario.Vertical.TScrollbar"', guide_source)
        self.assertIn('"game_livesplit_button"', guide_source)
        self.assertIn('"level_livesplit_button"', guide_source)
        self.assertIn("install_or_open_livesplit_copy", guide_source)

        assignment = next(
            node
            for node in self.tree.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name)
                and target.id == "SETUP_GUIDE_TRANSLATIONS"
                for target in node.targets
            )
        )
        translations = ast.literal_eval(assignment.value)
        english = translations["en"]["livesplit_obs_instructions"]
        self.assertIn("SELECT GAME LIVESPLIT", english)
        self.assertIn("SELECT LEVEL LIVESPLIT", english)
        self.assertIn("When the button turns green", english)
        self.assertIn("automatic TCP server startup", english)
        self.assertIn("You do not need to edit LiveSplit ports", english)
        self.assertIn("Save Settings", english)
        self.assertIn("ADD THE GAME TIMER TO OBS", english)
        self.assertIn("ADD THE LEVEL TIMER TO OBS", english)
        self.assertIn("Window Capture", english)
        self.assertIn("{game_port}", english)
        self.assertIn("{level_port}", english)
        self.assertNotIn("Right-click LiveSplit", english)
        self.assertNotIn("Start TCP/WS Server", english)

        for language in ("en", "au", "es", "fr", "de", "pt-BR"):
            with self.subTest(language=language):
                instructions = translations[language]["livesplit_obs_instructions"]
                self.assertIn("{game_port}", instructions)
                self.assertIn("{level_port}", instructions)
                self.assertIn("6.", instructions)

    def test_every_supported_language_has_setup_copy(self):
        assignment = next(
            node
            for node in self.tree.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name)
                and target.id == "SETUP_GUIDE_TRANSLATIONS"
                for target in node.targets
            )
        )
        translations = ast.literal_eval(assignment.value)
        required_keys = set(translations["en"])
        for language in ("es", "fr", "de", "pt-BR"):
            with self.subTest(language=language):
                self.assertFalse(required_keys.difference(translations[language]))
        self.assertIn("welcome_message", translations["au"])


if __name__ == "__main__":
    unittest.main()
