import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scheduler import (  # noqa: E402
    backtracking,
    brute_force,
    divide_and_conquer,
    dynamic_programming,
    grasp,
    greedy,
    load_instance,
    validate_schedule,
)


class SchedulerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.instance = load_instance(ROOT / "instances" / "exemplo.json")

    def test_all_algorithms_return_valid_schedule(self):
        for algorithm in (brute_force, backtracking, divide_and_conquer, dynamic_programming, greedy, grasp):
            with self.subTest(algorithm=algorithm.__name__):
                result = algorithm(self.instance)
                valid, errors = validate_schedule(self.instance, result.schedule)
                self.assertTrue(valid, errors)

    def test_exact_algorithms_agree(self):
        values = {
            brute_force(self.instance).makespan,
            backtracking(self.instance).makespan,
            dynamic_programming(self.instance).makespan,
        }
        self.assertEqual(len(values), 1)

    def test_deadline_decision(self):
        feasible = greedy(self.instance)
        self.assertLessEqual(feasible.makespan, self.instance.deadline)
        impossible = load_instance(ROOT / "instances" / "inviavel.json")
        optimum = dynamic_programming(impossible)
        self.assertGreater(optimum.makespan, impossible.deadline)


if __name__ == "__main__":
    unittest.main()

