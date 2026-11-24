import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "panel-peluditos"))

import google_forms
import negocio


class GoogleFormsTest(unittest.TestCase):
    def setUp(self):
        folder = self.enterContext(tempfile.TemporaryDirectory())
        data = Path(folder)
        self.enterContext(patch.multiple(negocio, DB=data / "negocio.sqlite3", DATA=data))
        self.enterContext(patch.multiple(google_forms,
                                         EXEC_URL="https://script.google.com/macros/s/test/exec",
                                         SYNC_KEY="a" * 64))
        negocio.initialize()
        self.started = set()
        self.answer = {"nombre": "Ana", "wsp": "+56911111111", "email": "ana@example.com",
                       "canal": "Instagram", "tipoMascota": "Gato", "mascota": "Luna",
                       "cumple": "2022-11-19", "fechaMs": 1, "id": "a"}

    def start(self, lead, deduplicate):
        self.assertTrue(deduplicate)
        created = lead["id"] not in self.started
        self.started.add(lead["id"])
        return lead["id"], created

    def test_importa_respuestas_en_orden_y_omite_la_invalida(self):
        batch = {"formId": "form", "respuestas": [
            self.answer, dict(self.answer, id="b", email="sin-arroba"),
            dict(self.answer, id="c")
        ]}
        with patch.object(google_forms, "fetch", return_value=batch):
            self.assertEqual(google_forms.synchronize(self.start),
                             {"status": "ok", "imported": 2, "skipped": 1, "more": False})
            self.assertEqual(google_forms.synchronize(self.start)["imported"], 0)
        self.assertEqual(len(self.started), 2)

    def test_reintenta_si_flowable_confirmo_antes_de_guardar_el_cursor(self):
        batch = {"formId": "form", "respuestas": [self.answer]}
        with patch.object(google_forms, "fetch", return_value=batch):
            with patch.object(negocio, "save_google_cursor", side_effect=RuntimeError("sin escritura")):
                with self.assertRaises(RuntimeError):
                    google_forms.synchronize(self.start)
            self.assertEqual(google_forms.synchronize(self.start)["imported"], 0)
        self.assertEqual(len(self.started), 1)


if __name__ == "__main__":
    unittest.main()
