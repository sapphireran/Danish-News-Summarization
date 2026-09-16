import unittest

from danish_summarization.pipeline_notes import STAGES, format_all_stages, format_stage


class PipelineNoteTests(unittest.TestCase):
    def test_every_root_script_is_documented(self):
        scripts = {stage.script for stage in STAGES}
        self.assertEqual(
            scripts,
            {
                "Ctranslate_converter.py",
                "translate.py",
                "summary.py",
                "translate_back.py",
                "finetune.py",
                "use_model.py",
                "eval.py",
            },
        )

    def test_format_stage_includes_caveats(self):
        text = format_stage(STAGES[0])
        self.assertIn("Ctranslate_converter.py", text)
        self.assertIn("caveats:", text)

    def test_format_all_stages_keeps_script_order(self):
        text = format_all_stages()
        positions = [text.index(stage.script) for stage in STAGES]
        self.assertEqual(positions, sorted(positions))


if __name__ == "__main__":
    unittest.main()
