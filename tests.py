"""Used to test the construction of graphs and general use of graphs"""

import copy
import unittest

import arrow
import mock
import networkx

from builder.tests_jobs import UpdateTargetCacheBottom, UpdateTargetCacheMiddle03, UpdateTargetCacheMiddle02, UpdateTargetCacheMiddle01, ForceBuildBottom, ForceBuildMiddle, ForceBuildTop, ExpandExactBottom, ExpandExactMiddle, ExpandExactTop, UpdateJobCacheBottom, UpdateJobCacheMiddle03, UpdateJobCacheMiddle02, UpdateJobCacheMiddle01, UpdateJobCacheTop, GetNextJobsToRunLowest, GetNextJobsToRunBottom, GetNextJobsToRunMiddle02, GetNextJobsToRunMiddle01, GetNextJobsToRunTop, UpdateLowerNodesShouldRunLowest, UpdateLowerNodesShouldRunBottom, UpdateLowerNodesShouldRunMiddle02, UpdateLowerNodesShouldRunMiddle01, UpdateLowerNodesShouldRunTop, GetStartingJobs04Tester, GetStartingJobs03Tester, GetStartingJobs02Tester, GetStartingJobs01Tester, ShouldRunRecurseJob10Tester, ShouldRunRecurseJob09Tester, ShouldRunRecurseJob08Tester, ShouldRunRecurseJob07Tester, ShouldRunRecurseJob06Tester, ShouldRunRecurseJob05Tester, ShouldRunRecurseJob04Tester, ShouldRunRecurseJob03Tester, ShouldRunRecurseJob02Tester, ShouldRunRecurseJob01Tester, ShouldRunCacheLogicJobTester, ShouldRunLogicJobTester, PastCurfewJobTester, AllDependenciesJobTester, PastCacheTimeJobTester, BuildableJobTester, StaleAlternateUpdateBottomJobTester, StaleAlternateUpdateTopJobTester, StaleAlternateBottomJobTester, StaleAlternateTopJobTester, StaleIgnoreMtimeJobTester, StaleStandardJobTester, DiamondRedundancyHighestJobTester, DiamondRedundancyTopJobTester, DiamondRedundancyMiddleJob02Tester, DiamondRedundancyMiddleJob01Tester, DiamondRedundancyBottomJobTester, BackboneDependantTopJob02Tester, BackboneDependantTopJob01Tester, BackboneDependantMiddleJob02Tester, BackboneDependantMiddleJob01Tester, BackboneDependantBottomJobTester, BuildGraphConstructionJobBottom01Tester, BuildGraphConstructionJobTop02Tester, BuildGraphConstructionJobTop01Tester, RuleDepConstructionJobBottom01Tester, RuleDepConstructionJobTop02Tester, RuleDepConstructionJobTop01Tester, UpdateTargetCacheTop, PastCurfewTimestampJobTester
import testing
import builder.jobs
import builder.build


class GraphTest(unittest.TestCase):
    """Used to test the general graph construction"""
    @staticmethod
    def mock_mtime_generator(file_dict):
        """Used to generate a fake os.stat

        takes in a list of files and returns a function that will return the
        mtime corresponding to the path passed to it
        """
        def mock_mtime(path):
            """Returns the mtime corresponding to the path

            raises:
                OSError: if the path is not in the file_dict
            """
            if path not in file_dict:
                raise OSError(2, "No such file or directory")
            mock_stat = mock.Mock()
            mock_stat.st_mtime = file_dict[path]
            return mock_stat
        return mock_mtime

    @testing.unit
    def test_rule_dep_construction(self):
        # Given
        jobs = [
            RuleDepConstructionJobTop01Tester(),
            RuleDepConstructionJobTop02Tester(),
            RuleDepConstructionJobBottom01Tester(),
        ]

        expected_edges = (
            ("rule_dep_construction_target_highest_02",
             "rule_dep_construction_job_top_02",
             {"label": "depends"}),
            ("rule_dep_construction_target_highest_02",
             "rule_dep_construction_job_top_02",
             {"label": "depends"}),
            ("rule_dep_construction_target_highest_03",
             "rule_dep_construction_job_top_02",
             {"label": "depends"}),
            ("rule_dep_construction_target_highest_04",
             "rule_dep_construction_job_top_02",
             {"label": "depends_one_or_more"}),
            ("rule_dep_construction_job_top_02",
             "rule_dep_construction_target_top_02",
             {"label": "produces"}),
            ("rule_dep_construction_job_top_02",
             "rule_dep_construction_target_top_03",
             {"label": "produces"}),
            ("rule_dep_construction_job_top_02",
             "rule_dep_construction_target_top_04",
             {"label": "alternates"}),
            ("rule_dep_construction_target_top_02",
             "rule_dep_construction_job_bottom_01",
             {"label": "depends"}),
            ("rule_dep_construction_target_top_03",
             "rule_dep_construction_job_bottom_01",
             {"label": "depends"}),
            ("rule_dep_construction_target_top_04",
             "rule_dep_construction_job_bottom_01",
             {"label": "depends_one_or_more"}),
            ("rule_dep_construction_job_bottom_01",
             "rule_dep_construction_target_bottom_01",
             {"label": "produces"}),
        )

        graph = builder.build.Build(jobs)

        # When
        graph.construct_rule_dependency_graph()
        rule_dep_graph = graph.rule_dep_graph

        # Then
        for expected_edge in expected_edges:
            for actual_edge in rule_dep_graph.edges_iter(data=True):
                if expected_edge == actual_edge:
                    break
            else:
                self.assertTrue(
                        False,
                        msg="{} is not in the graph".format(expected_edge))

    @testing.unit
    def test_build_plan_construction(self):
        # Given
        jobs = [
            BuildGraphConstructionJobTop01Tester(),
            BuildGraphConstructionJobTop02Tester(),
            BuildGraphConstructionJobBottom01Tester(),
        ]

        start_time = "2014-12-05T10:30"
        start_time = arrow.get(start_time)
        end_time = "2014-12-05T11:30"
        end_time = arrow.get(end_time)

        start_job1 = "build_graph_construction_job_bottom_01"
        start_job2 = "build_graph_construction_job_top_01"

        build_context1 = {
                "start_time": start_time,
                "end_time": end_time,
                "start_job": start_job1
        }
        build_context2 = {
                "start_time": start_time,
                "end_time": end_time,
                "start_job": start_job2
        }

        node1_id = "build_graph_construction_job_top_01_2014-12-05-10-30"
        node2_id = "build_graph_construction_job_top_01_2014-12-05-11-25"
        node3_id = "build_graph_construction_job_top_02_2014-12-05-10-00"
        node4_id = "build_graph_construction_job_top_02_2014-12-05-10-55"
        node5_id = "build_graph_construction_job_bottom_01_2014-12-05-10-00"

        expected_number_of_parents1 = 1
        expected_number_of_parents2 = 1
        expected_number_of_parents3 = 3
        expected_number_of_parents4 = 3
        expected_number_of_parents5 = 3

        expected_number_of_dependencies1 = 5
        expected_number_of_dependencies2 = 5
        expected_number_of_dependencies3 = 11
        expected_number_of_dependencies4 = 11
        expected_number_of_dependencies5 = 60 + 12 + 3 + 12

        expected_number_of_targets1 = 1
        expected_number_of_targets2 = 1
        expected_number_of_targets3 = 7
        expected_number_of_targets4 = 7
        expected_number_of_targets5 = 12

        # When
        build = builder.build.Build(jobs)

        build.construct_build_graph(build_context1)
        build.construct_build_graph(build_context2)

        build_graph = build

        depends1 = build_graph.predecessors(node1_id)
        depends2 = build_graph.predecessors(node2_id)
        depends3 = build_graph.predecessors(node3_id)
        depends4 = build_graph.predecessors(node4_id)
        depends5 = build_graph.predecessors(node5_id)

        number_of_parents1 = len(depends1)
        number_of_parents2 = len(depends2)
        number_of_parents3 = len(depends3)
        number_of_parents4 = len(depends4)
        number_of_parents5 = len(depends5)

        number_of_dependencies1 = 0
        for depends in depends1:
            number_of_dependencies1 = (number_of_dependencies1 +
                    len(build_graph.predecessors(depends)))
        number_of_dependencies2 = 0
        for depends in depends2:
            number_of_dependencies2 = (number_of_dependencies2 +
                    len(build_graph.predecessors(depends)))
        number_of_dependencies3 = 0
        for depends in depends3:
            number_of_dependencies3 = (number_of_dependencies3 +
                    len(build_graph.predecessors(depends)))
        number_of_dependencies4 = 0
        for depends in depends4:
            number_of_dependencies4 = (number_of_dependencies4 +
                    len(build_graph.predecessors(depends)))
        number_of_dependencies5 = 0
        for depends in depends5:
            number_of_dependencies5 = (number_of_dependencies5 +
                    len(build_graph.predecessors(depends)))

        targets1 = build_graph.neighbors(node1_id)
        targets2 = build_graph.neighbors(node2_id)
        targets3 = build_graph.neighbors(node3_id)
        targets4 = build_graph.neighbors(node4_id)
        targets5 = build_graph.neighbors(node5_id)

        number_of_targets1 = len(targets1)
        number_of_targets2 = len(targets2)
        number_of_targets3 = len(targets3)
        number_of_targets4 = len(targets4)
        number_of_targets5 = len(targets5)

        # Then
        self.assertIn(node1_id, build_graph.nodes())
        self.assertIn(node2_id, build_graph.nodes())
        self.assertIn(node3_id, build_graph.nodes())
        self.assertIn(node4_id, build_graph.nodes())
        self.assertIn(node5_id, build_graph.nodes())

        self.assertEqual(expected_number_of_parents1, number_of_parents1)
        self.assertEqual(expected_number_of_parents2, number_of_parents2)
        self.assertEqual(expected_number_of_parents3, number_of_parents3)
        self.assertEqual(expected_number_of_parents4, number_of_parents4)
        self.assertEqual(expected_number_of_parents5, number_of_parents5)

        self.assertEqual(number_of_dependencies1,
                         expected_number_of_dependencies1)
        self.assertEqual(number_of_dependencies2,
                         expected_number_of_dependencies2)
        self.assertEqual(number_of_dependencies3,
                         expected_number_of_dependencies3)
        self.assertEqual(number_of_dependencies4,
                         expected_number_of_dependencies4)
        self.assertEqual(number_of_dependencies5,
                         expected_number_of_dependencies5)

        self.assertEqual(expected_number_of_targets1, number_of_targets1)
        self.assertEqual(expected_number_of_targets2, number_of_targets2)
        self.assertEqual(expected_number_of_targets3, number_of_targets3)
        self.assertEqual(expected_number_of_targets4, number_of_targets4)
        self.assertEqual(expected_number_of_targets5, number_of_targets5)

    @testing.unit
    def test_backbone_dependant(self):
        # Given
        config1 = {
                "has_backbone": True,
        }
        config2 = {
                "has_backbone": False,
        }

        jobs1 = [
            BackboneDependantBottomJobTester(config=config1),
            BackboneDependantMiddleJob01Tester(config=config1),
            BackboneDependantMiddleJob02Tester(config=config1),
            BackboneDependantTopJob01Tester(config=config1),
            BackboneDependantTopJob02Tester(config=config1),
        ]

        jobs2 = [
            BackboneDependantBottomJobTester(config=config2),
            BackboneDependantMiddleJob01Tester(config=config2),
            BackboneDependantMiddleJob02Tester(config=config2),
            BackboneDependantTopJob01Tester(config=config2),
            BackboneDependantTopJob02Tester(config=config2),
        ]

        build_context1 = {
                "start_time": arrow.get("2014-12-05T10:50"),
                "end_time": arrow.get("2014-12-05T10:55"),
                "start_job": "backbone_dependant_bottom_job",
        }
        build_context2 = {
                "start_time": arrow.get("2014-12-05T10:50"),
                "end_time": arrow.get("2014-12-05T10:55"),
                "start_job": "backbone_dependant_bottom_job",
        }

        build1 = builder.build.Build(jobs1, config=config1)
        build2 = builder.build.Build(jobs2, config=config2)

        expected_build_count1 = 18
        expected_build_count2 = 10

        middle_node_01 = "backbone_dependant_middle_job_01"
        middle_node_02 = "backbone_dependant_middle_job_02"
        top_node_01 = "backbone_dependant_top_job_01"
        top_node_02 = "backbone_dependant_top_job_02"

        # When
        build1.construct_build_graph(build_context1)
        build2.construct_build_graph(build_context2)

        build_count1 = len(build1.nodes())
        build_count2 = len(build2.nodes())

        # Then
        self.assertEqual(build_count1, expected_build_count1)
        self.assertEqual(build_count2, expected_build_count2)
        self.assertIn(middle_node_01, build1.nodes())
        self.assertIn(middle_node_02, build1.nodes())
        self.assertIn(top_node_01, build1.nodes())
        self.assertIn(top_node_02, build1.nodes())
        self.assertNotIn(middle_node_01, build2.nodes())
        self.assertIn(middle_node_02, build2.nodes())
        self.assertNotIn(top_node_01, build2.nodes())
        self.assertIn(top_node_02, build2.nodes())

    @testing.unit
    def test_diamond_redundancy(self):
        # Given
        jobs = [
            DiamondRedundancyBottomJobTester(),
            DiamondRedundancyMiddleJob01Tester(),
            DiamondRedundancyMiddleJob02Tester(),
            DiamondRedundancyTopJobTester(),
            DiamondRedundancyHighestJobTester(),
        ]

        build_context = {
           "start_time": arrow.get("2014-12-05T10:50"),
           "end_time": arrow.get("2014-12-05T10:55"),
           "start_job": "diamond_redundant_bottom_job",
        }

        build = builder.build.Build(jobs)

        expected_call_count1 = 1
        expected_call_count2 = 1
        expected_call_count3 = 3
        expected_call_count4 = 2
        expected_call_count5 = 1

        # When
        build.construct_build_graph(build_context)
        call_count1 = (DiamondRedundancyTopJobTester.count)
        call_count2 = (DiamondRedundancyHighestJobTester.count)
        call_count3 = (build.rule_dep_graph.node
                ["diamond_redundancy_top_target"]
                ["object"]
                .count)
        call_count4 = (build.rule_dep_graph.node
                ["diamond_redundancy_highest_target"]
                ["object"]
                .count)
        call_count5 = (build.rule_dep_graph.node
                ["diamond_redundancy_super_target"]
                ["object"]
                .count)

        # Then
        self.assertEqual(call_count1, expected_call_count1)
        self.assertEqual(call_count2, expected_call_count2)
        self.assertEqual(call_count3, expected_call_count3)
        self.assertEqual(call_count4, expected_call_count4)
        self.assertEqual(call_count5, expected_call_count5)

    @testing.unit
    def test_stale(self):
        # Given
        current_time = 600
        jobs1 = [
            StaleStandardJobTester(),
        ]

        jobs2 = [
            StaleIgnoreMtimeJobTester(),
        ]

        build_context1 = {
            "start_time": arrow.get("2014-12-05T10:50"),
            "end_time": arrow.get("2014-12-05T10:50"),
            "start_job": "stale_standard_job", # StaleStandardJobTester,
        }

        build_context2 = {
            "start_time": arrow.get("2014-12-05T10:50"),
            "end_time": arrow.get("2014-12-05T10:50"),
            "start_job": "stale_ignore_mtime_job", # StaleIgnoreMtimeJobTester,
        }

        build1 = builder.build.Build(jobs1)
        build2 = builder.build.Build(jobs1)
        build3 = builder.build.Build(jobs1)
        build4 = builder.build.Build(jobs1)
        build5 = builder.build.Build(jobs1)
        build6 = builder.build.Build(jobs2)
        build7 = builder.build.Build(jobs2)

        build1.construct_build_graph(copy.deepcopy(build_context1))
        build2.construct_build_graph(copy.deepcopy(build_context1))
        build3.construct_build_graph(copy.deepcopy(build_context1))
        build4.construct_build_graph(copy.deepcopy(build_context1))
        build5.construct_build_graph(copy.deepcopy(build_context1))
        build6.construct_build_graph(copy.deepcopy(build_context2))
        build7.construct_build_graph(copy.deepcopy(build_context2))

        # all deps, all targets, all deps are older than targets
        expected_stale1 = False
        (build1.node
                ["stale_top_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build1.node
                ["stale_top_target-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build1.node
                ["stale_top_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build1.node
                ["stale_top_target-2014-12-05-10-50"]
                ["object"].mtime) = 100
        (build1.node
                ["stale_top_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build1.node
                ["stale_top_target-2014-12-05-10-55"]
                ["object"].mtime) = 100
        (build1.node
                ["stale_standard_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build1.node
                ["stale_standard_target-2014-12-05-10-45"]
                ["object"].mtime) = 150
        (build1.node
                ["stale_standard_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build1.node
                ["stale_standard_target-2014-12-05-10-50"]
                ["object"].mtime) = 150
        (build1.node
                ["stale_standard_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build1.node
                ["stale_standard_target-2014-12-05-10-55"]
                ["object"].mtime) = 150
        # not buildable, still not stale
        expected_stale2 = False
        (build2.node
                ["stale_top_target-2014-12-05-10-45"]
                ["object"].exists) = False
        (build2.node
                ["stale_top_target-2014-12-05-10-45"]
                ["object"].mtime) = None
        (build2.node
                ["stale_top_target-2014-12-05-10-50"]
                ["object"].exists) = False
        (build2.node
                ["stale_top_target-2014-12-05-10-50"]
                ["object"].mtime) = None
        (build2.node
                ["stale_top_target-2014-12-05-10-55"]
                ["object"].exists) = False
        (build2.node
                ["stale_top_target-2014-12-05-10-55"]
                ["object"].mtime) = None
        (build2.node
                ["stale_standard_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build2.node
                ["stale_standard_target-2014-12-05-10-45"]
                ["object"].mtime) = 150
        (build2.node
                ["stale_standard_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build2.node
                ["stale_standard_target-2014-12-05-10-50"]
                ["object"].mtime) = 150
        (build2.node
                ["stale_standard_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build2.node
                ["stale_standard_target-2014-12-05-10-55"]
                ["object"].mtime) = 150
        # all deps, all targets, one dep newer than one target
        expected_stale3 = True
        (build3.node
                ["stale_top_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build3.node
                ["stale_top_target-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build3.node
                ["stale_top_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build3.node
                ["stale_top_target-2014-12-05-10-50"]
                ["object"].mtime) = 100
        (build3.node
                ["stale_top_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build3.node
                ["stale_top_target-2014-12-05-10-55"]
                ["object"].mtime) = 120
        (build3.node
                ["stale_standard_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build3.node
                ["stale_standard_target-2014-12-05-10-45"]
                ["object"].mtime) = 150
        (build3.node
                ["stale_standard_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build3.node
                ["stale_standard_target-2014-12-05-10-50"]
                ["object"].mtime) = 150
        (build3.node
                ["stale_standard_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build3.node
                ["stale_standard_target-2014-12-05-10-55"]
                ["object"].mtime) = 110
        # all deps, one missing target, all targets newer than deps
        expected_stale4 = True
        (build4.node
                ["stale_top_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build4.node
                ["stale_top_target-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build4.node
                ["stale_top_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build4.node
                ["stale_top_target-2014-12-05-10-50"]
                ["object"].mtime) = 100
        (build4.node
                ["stale_top_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build4.node
                ["stale_top_target-2014-12-05-10-55"]
                ["object"].mtime) = 100
        (build4.node
                ["stale_standard_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build4.node
                ["stale_standard_target-2014-12-05-10-45"]
                ["object"].mtime) = 150
        (build4.node
                ["stale_standard_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build4.node
                ["stale_standard_target-2014-12-05-10-50"]
                ["object"].mtime) = 150
        (build4.node
                ["stale_standard_target-2014-12-05-10-55"]
                ["object"].exists) = False
        (build4.node
                ["stale_standard_target-2014-12-05-10-55"]
                ["object"].mtime) = None
        # all targets are within the cache_time
        expected_stale5 = False
        (build5.node
                ["stale_top_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build5.node
                ["stale_top_target-2014-12-05-10-45"]
                ["object"].mtime) = 600
        (build5.node
                ["stale_top_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build5.node
                ["stale_top_target-2014-12-05-10-50"]
                ["object"].mtime) = 600
        (build5.node
                ["stale_top_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build5.node
                ["stale_top_target-2014-12-05-10-55"]
                ["object"].mtime) = 600
        (build5.node
                ["stale_standard_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build5.node
                ["stale_standard_target-2014-12-05-10-45"]
                ["object"].mtime) = 500
        (build5.node
                ["stale_standard_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build5.node
                ["stale_standard_target-2014-12-05-10-50"]
                ["object"].mtime) = 500
        (build5.node
                ["stale_standard_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build5.node
                ["stale_standard_target-2014-12-05-10-55"]
                ["object"].mtime) = 500
        # target is older than an ignored mtime
        expected_stale6 = False
        (build6.node
                ["stale_ignore_mtime_input_target_01-2014-12-05-10-45"]
                ["object"].exists) = True
        (build6.node
                ["stale_ignore_mtime_input_target_01-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build6.node
                ["stale_ignore_mtime_input_target_01-2014-12-05-10-50"]
                ["object"].exists) = True
        (build6.node
                ["stale_ignore_mtime_input_target_01-2014-12-05-10-50"]
                ["object"].mtime) = 100
        (build6.node
                ["stale_ignore_mtime_input_target_01-2014-12-05-10-55"]
                ["object"].exists) = True
        (build6.node
                ["stale_ignore_mtime_input_target_01-2014-12-05-10-55"]
                ["object"].mtime) = 100
        (build6.node
                ["stale_ignore_mtime_input_target_02-2014-12-05-10-45"]
                ["object"].exists) = True
        (build6.node
                ["stale_ignore_mtime_input_target_02-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build6.node
                ["stale_ignore_mtime_input_target_02-2014-12-05-10-50"]
                ["object"].exists) = True
        (build6.node
                ["stale_ignore_mtime_input_target_02-2014-12-05-10-50"]
                ["object"].mtime) = 120
        (build6.node
                ["stale_ignore_mtime_input_target_02-2014-12-05-10-55"]
                ["object"].exists) = True
        (build6.node
                ["stale_ignore_mtime_input_target_02-2014-12-05-10-55"]
                ["object"].mtime) = 100
        (build6.node
                ["stale_ignore_mtime_output_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build6.node
                ["stale_ignore_mtime_output_target-2014-12-05-10-45"]
                ["object"].mtime) = 150
        (build6.node
                ["stale_ignore_mtime_output_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build6.node
                ["stale_ignore_mtime_output_target-2014-12-05-10-50"]
                ["object"].mtime) = 150
        (build6.node
                ["stale_ignore_mtime_output_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build6.node
                ["stale_ignore_mtime_output_target-2014-12-05-10-55"]
                ["object"].mtime) = 110
        # target is older than an non ignored mtime
        expected_stale7 = True
        (build7.node
                ["stale_ignore_mtime_input_target_01-2014-12-05-10-45"]
                ["object"].exists) = True
        (build7.node
                ["stale_ignore_mtime_input_target_01-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build7.node
                ["stale_ignore_mtime_input_target_01-2014-12-05-10-50"]
                ["object"].exists) = True
        (build7.node
                ["stale_ignore_mtime_input_target_01-2014-12-05-10-50"]
                ["object"].mtime) = 120
        (build7.node
                ["stale_ignore_mtime_input_target_01-2014-12-05-10-55"]
                ["object"].exists) = True
        (build7.node
                ["stale_ignore_mtime_input_target_01-2014-12-05-10-55"]
                ["object"].mtime) = 100
        (build7.node
                ["stale_ignore_mtime_input_target_02-2014-12-05-10-45"]
                ["object"].exists) = True
        (build7.node
                ["stale_ignore_mtime_input_target_02-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build7.node
                ["stale_ignore_mtime_input_target_02-2014-12-05-10-50"]
                ["object"].exists) = True
        (build7.node
                ["stale_ignore_mtime_input_target_02-2014-12-05-10-50"]
                ["object"].mtime) = 120
        (build7.node
                ["stale_ignore_mtime_input_target_02-2014-12-05-10-55"]
                ["object"].exists) = True
        (build7.node
                ["stale_ignore_mtime_input_target_02-2014-12-05-10-55"]
                ["object"].mtime) = 100
        (build7.node
                ["stale_ignore_mtime_output_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build7.node
                ["stale_ignore_mtime_output_target-2014-12-05-10-45"]
                ["object"].mtime) = 150
        (build7.node
                ["stale_ignore_mtime_output_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build7.node
                ["stale_ignore_mtime_output_target-2014-12-05-10-50"]
                ["object"].mtime) = 150
        (build7.node
                ["stale_ignore_mtime_output_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build7.node
                ["stale_ignore_mtime_output_target-2014-12-05-10-55"]
                ["object"].mtime) = 110


        old_arrow_get = copy.deepcopy(arrow.get)
        def new_arrow_get(*args, **kwargs):
            """This wraps the original arrow get so we can override only
            arrow get with no args
            """
            if not args and not kwargs:
                return arrow.get(current_time)
            else:
                return old_arrow_get(*args, **kwargs)


        # When
        with mock.patch("arrow.get", new_arrow_get):
            stale1 = (build1.node
                    ["stale_standard_job_2014-12-05-10-45"]
                    ["object"].get_stale(build1))
            stale2 = (build2.node
                    ["stale_standard_job_2014-12-05-10-45"]
                    ["object"].get_stale(build2))
            stale3 = (build3.node
                    ["stale_standard_job_2014-12-05-10-45"]
                    ["object"].get_stale(build3))
            stale4 = (build4.node
                    ["stale_standard_job_2014-12-05-10-45"]
                    ["object"].get_stale(build4))
            stale5 = (build5.node
                    ["stale_standard_job_2014-12-05-10-45"]
                    ["object"].get_stale(build5))
            stale6 = (build6.node
                    ["stale_ignore_mtime_job_2014-12-05-10-45"]
                    ["object"].get_stale(build6))
            stale7 = (build7.node
                    ["stale_ignore_mtime_job_2014-12-05-10-45"]
                    ["object"].get_stale(build7))

        # Then
        self.assertEqual(stale1, expected_stale1)
        self.assertEqual(stale2, expected_stale2)
        self.assertEqual(stale3, expected_stale3)
        self.assertEqual(stale4, expected_stale4)
        self.assertEqual(stale5, expected_stale5)
        self.assertEqual(stale6, expected_stale6)
        self.assertEqual(stale7, expected_stale7)

    @testing.unit
    def test_stale_alternate(self):
        # Given
        jobs1 = [
            StaleAlternateTopJobTester(),
            StaleAlternateBottomJobTester(),
        ]

        build_context1 = {
            "start_time": arrow.get("2014-12-05T10:50"),
            "end_time": arrow.get("2014-12-05T10:50"),
            "start_job": "stale_alternate_bottom_job", # StaleAlternateBottomJobTester,
        }

        build1 = builder.build.Build(jobs1)
        build2 = builder.build.Build(jobs1)
        build3 = builder.build.Build(jobs1)
        build4 = builder.build.Build(jobs1)

        build1.construct_build_graph(copy.deepcopy(build_context1))
        build2.construct_build_graph(copy.deepcopy(build_context1))
        build3.construct_build_graph(copy.deepcopy(build_context1))
        build4.construct_build_graph(copy.deepcopy(build_context1))

        # All alternates exist and are stale but the targets are not
        expected_stale1 = False
        (build1.node
                ["stale_alternate_highest_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build1.node
                ["stale_alternate_highest_target-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build1.node
                ["stale_alternate_highest_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build1.node
                ["stale_alternate_highest_target-2014-12-05-10-50"]
                ["object"].mtime) = 100
        (build1.node
                ["stale_alternate_highest_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build1.node
                ["stale_alternate_highest_target-2014-12-05-10-55"]
                ["object"].mtime) = 100
        (build1.node
                ["stale_alternate_top_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build1.node
                ["stale_alternate_top_target-2014-12-05-10-45"]
                ["object"].mtime) = 150
        (build1.node
                ["stale_alternate_top_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build1.node
                ["stale_alternate_top_target-2014-12-05-10-50"]
                ["object"].mtime) = 150
        (build1.node
                ["stale_alternate_top_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build1.node
                ["stale_alternate_top_target-2014-12-05-10-55"]
                ["object"].mtime) = 150
        (build1.node
                ["stale_alternate_secondary_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build1.node
                ["stale_alternate_secondary_target-2014-12-05-10-45"]
                ["object"].mtime) = 150
        (build1.node
                ["stale_alternate_secondary_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build1.node
                ["stale_alternate_secondary_target-2014-12-05-10-50"]
                ["object"].mtime) = 150
        (build1.node
                ["stale_alternate_secondary_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build1.node
                ["stale_alternate_secondary_target-2014-12-05-10-55"]
                ["object"].mtime) = 150
        (build1.node
                ["stale_alternate_bottom_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build1.node
                ["stale_alternate_bottom_target-2014-12-05-10-45"]
                ["object"].mtime) = 50
        (build1.node
                ["stale_alternate_bottom_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build1.node
                ["stale_alternate_bottom_target-2014-12-05-10-50"]
                ["object"].mtime) = 50
        (build1.node
                ["stale_alternate_bottom_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build1.node
                ["stale_alternate_bottom_target-2014-12-05-10-55"]
                ["object"].mtime) = 50

        # All alternates exist and are stale but the targets are not
        # and a single target does not exist
        expected_stale2 = False
        (build2.node
                ["stale_alternate_highest_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build2.node
                ["stale_alternate_highest_target-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build2.node
                ["stale_alternate_highest_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build2.node
                ["stale_alternate_highest_target-2014-12-05-10-50"]
                ["object"].mtime) = 100
        (build2.node
                ["stale_alternate_highest_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build2.node
                ["stale_alternate_highest_target-2014-12-05-10-55"]
                ["object"].mtime) = 100
        (build2.node
                ["stale_alternate_top_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build2.node
                ["stale_alternate_top_target-2014-12-05-10-45"]
                ["object"].mtime) = 150
        (build2.node
                ["stale_alternate_top_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build2.node
                ["stale_alternate_top_target-2014-12-05-10-50"]
                ["object"].mtime) = 150
        (build2.node
                ["stale_alternate_top_target-2014-12-05-10-55"]
                ["object"].exists) = False
        (build2.node
                ["stale_alternate_top_target-2014-12-05-10-55"]
                ["object"].mtime) = None
        (build2.node
                ["stale_alternate_secondary_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build2.node
                ["stale_alternate_secondary_target-2014-12-05-10-45"]
                ["object"].mtime) = 150
        (build2.node
                ["stale_alternate_secondary_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build2.node
                ["stale_alternate_secondary_target-2014-12-05-10-50"]
                ["object"].mtime) = 150
        (build2.node
                ["stale_alternate_secondary_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build2.node
                ["stale_alternate_secondary_target-2014-12-05-10-55"]
                ["object"].mtime) = 150
        (build2.node
                ["stale_alternate_bottom_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build2.node
                ["stale_alternate_bottom_target-2014-12-05-10-45"]
                ["object"].mtime) = 50
        (build2.node
                ["stale_alternate_bottom_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build2.node
                ["stale_alternate_bottom_target-2014-12-05-10-50"]
                ["object"].mtime) = 50
        (build2.node
                ["stale_alternate_bottom_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build2.node
                ["stale_alternate_bottom_target-2014-12-05-10-55"]
                ["object"].mtime) = 50

        # All alternates exist and are stale but the targets are not
        # and a single alternate does not exist
        expected_stale3 = False
        (build3.node
                ["stale_alternate_highest_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build3.node
                ["stale_alternate_highest_target-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build3.node
                ["stale_alternate_highest_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build3.node
                ["stale_alternate_highest_target-2014-12-05-10-50"]
                ["object"].mtime) = 100
        (build3.node
                ["stale_alternate_highest_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build3.node
                ["stale_alternate_highest_target-2014-12-05-10-55"]
                ["object"].mtime) = 100
        (build3.node
                ["stale_alternate_top_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build3.node
                ["stale_alternate_top_target-2014-12-05-10-45"]
                ["object"].mtime) = 150
        (build3.node
                ["stale_alternate_top_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build3.node
                ["stale_alternate_top_target-2014-12-05-10-50"]
                ["object"].mtime) = 150
        (build3.node
                ["stale_alternate_top_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build3.node
                ["stale_alternate_top_target-2014-12-05-10-55"]
                ["object"].mtime) = 150
        (build3.node
                ["stale_alternate_secondary_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build3.node
                ["stale_alternate_secondary_target-2014-12-05-10-45"]
                ["object"].mtime) = 150
        (build3.node
                ["stale_alternate_secondary_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build3.node
                ["stale_alternate_secondary_target-2014-12-05-10-50"]
                ["object"].mtime) = 150
        (build3.node
                ["stale_alternate_secondary_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build3.node
                ["stale_alternate_secondary_target-2014-12-05-10-55"]
                ["object"].mtime) = 150
        (build3.node
                ["stale_alternate_bottom_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build3.node
                ["stale_alternate_bottom_target-2014-12-05-10-45"]
                ["object"].mtime) = 50
        (build3.node
                ["stale_alternate_bottom_target-2014-12-05-10-50"]
                ["object"].exists) = False
        (build3.node
                ["stale_alternate_bottom_target-2014-12-05-10-50"]
                ["object"].mtime) = None
        (build3.node
                ["stale_alternate_bottom_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build3.node
                ["stale_alternate_bottom_target-2014-12-05-10-55"]
                ["object"].mtime) = 50

        # All alternates exist and are stale but the targets are not
        # and a single alternate does not exist and a single target
        # (not corresponding) does not exist
        expected_stale4 = True
        (build4.node
                ["stale_alternate_highest_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build4.node
                ["stale_alternate_highest_target-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build4.node
                ["stale_alternate_highest_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build4.node
                ["stale_alternate_highest_target-2014-12-05-10-50"]
                ["object"].mtime) = 100
        (build4.node
                ["stale_alternate_highest_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build4.node
                ["stale_alternate_highest_target-2014-12-05-10-55"]
                ["object"].mtime) = 100
        (build4.node
                ["stale_alternate_top_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build4.node
                ["stale_alternate_top_target-2014-12-05-10-45"]
                ["object"].mtime) = 150
        (build4.node
                ["stale_alternate_top_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build4.node
                ["stale_alternate_top_target-2014-12-05-10-50"]
                ["object"].mtime) = 150
        (build4.node
                ["stale_alternate_top_target-2014-12-05-10-55"]
                ["object"].exists) = False
        (build4.node
                ["stale_alternate_top_target-2014-12-05-10-55"]
                ["object"].mtime) = None
        (build4.node
                ["stale_alternate_secondary_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build4.node
                ["stale_alternate_secondary_target-2014-12-05-10-45"]
                ["object"].mtime) = 150
        (build4.node
                ["stale_alternate_secondary_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build4.node
                ["stale_alternate_secondary_target-2014-12-05-10-50"]
                ["object"].mtime) = 150
        (build4.node
                ["stale_alternate_secondary_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build4.node
                ["stale_alternate_secondary_target-2014-12-05-10-55"]
                ["object"].mtime) = 150
        (build4.node
                ["stale_alternate_bottom_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build4.node
                ["stale_alternate_bottom_target-2014-12-05-10-45"]
                ["object"].mtime) = 50
        (build4.node
                ["stale_alternate_bottom_target-2014-12-05-10-50"]
                ["object"].exists) = False
        (build4.node
                ["stale_alternate_bottom_target-2014-12-05-10-50"]
                ["object"].mtime) = None
        (build4.node
                ["stale_alternate_bottom_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build4.node
                ["stale_alternate_bottom_target-2014-12-05-10-55"]
                ["object"].mtime) = 50

        # When
        stale1 = (build1.node
                ["stale_alternate_top_job_2014-12-05-10-45"]
                ["object"].get_stale(build1))
        stale2 = (build2.node
                ["stale_alternate_top_job_2014-12-05-10-45"]
                ["object"].get_stale(build2))
        stale3 = (build3.node
                ["stale_alternate_top_job_2014-12-05-10-45"]
                ["object"].get_stale(build3))
        stale4 = (build4.node
                ["stale_alternate_top_job_2014-12-05-10-45"]
                ["object"].get_stale(build4))

        # Then
        self.assertEqual(stale1, expected_stale1)
        self.assertEqual(stale2, expected_stale2)
        self.assertEqual(stale3, expected_stale3)
        self.assertEqual(stale4, expected_stale4)

    @testing.unit
    def test_stale_alternate_update(self):
        # Given
        jobs1 = [
            StaleAlternateUpdateTopJobTester(),
            StaleAlternateUpdateBottomJobTester(),
        ]

        build_context1 = {
            "start_time": arrow.get("2014-12-05T10:50"),
            "end_time": arrow.get("2014-12-05T10:50"),
            "start_job": "stale_alternate_update_bottom_job", # StaleAlternateUpdateBottomJobTester,
        }

        build1 = builder.build.Build(jobs1)
        build2 = builder.build.Build(jobs1)
        build3 = builder.build.Build(jobs1)
        build4 = builder.build.Build(jobs1)

        build1.construct_build_graph(copy.deepcopy(build_context1))
        build2.construct_build_graph(copy.deepcopy(build_context1))
        build3.construct_build_graph(copy.deepcopy(build_context1))
        build4.construct_build_graph(copy.deepcopy(build_context1))

        # All alternate_updates exist and are stale but the targets are not
        # All targets exist
        expected_original_stale1 = False
        expected_stale1 = False
        (build1.node
                ["stale_alternate_update_highest_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build1.node
                ["stale_alternate_update_highest_target-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build1.node
                ["stale_alternate_update_highest_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build1.node
                ["stale_alternate_update_highest_target-2014-12-05-10-50"]
                ["object"].mtime) = 100
        (build1.node
                ["stale_alternate_update_highest_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build1.node
                ["stale_alternate_update_highest_target-2014-12-05-10-55"]
                ["object"].mtime) = 100
        (build1.node
                ["stale_alternate_update_top_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build1.node
                ["stale_alternate_update_top_target-2014-12-05-10-45"]
                ["object"].mtime) = 150
        (build1.node
                ["stale_alternate_update_top_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build1.node
                ["stale_alternate_update_top_target-2014-12-05-10-50"]
                ["object"].mtime) = 150
        (build1.node
                ["stale_alternate_update_top_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build1.node
                ["stale_alternate_update_top_target-2014-12-05-10-55"]
                ["object"].mtime) = 150
        (build1.node
                ["stale_alternate_update_secondary_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build1.node
                ["stale_alternate_update_secondary_target-2014-12-05-10-45"]
                ["object"].mtime) = 150
        (build1.node
                ["stale_alternate_update_secondary_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build1.node
                ["stale_alternate_update_secondary_target-2014-12-05-10-50"]
                ["object"].mtime) = 150
        (build1.node
                ["stale_alternate_update_secondary_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build1.node
                ["stale_alternate_update_secondary_target-2014-12-05-10-55"]
                ["object"].mtime) = 150
        (build1.node
                ["stale_alternate_update_bottom_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build1.node
                ["stale_alternate_update_bottom_target-2014-12-05-10-45"]
                ["object"].mtime) = 50
        (build1.node
                ["stale_alternate_update_bottom_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build1.node
                ["stale_alternate_update_bottom_target-2014-12-05-10-50"]
                ["object"].mtime) = 50
        (build1.node
                ["stale_alternate_update_bottom_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build1.node
                ["stale_alternate_update_bottom_target-2014-12-05-10-55"]
                ["object"].mtime) = 50

        # All alternate_updates exist and are stale but the targets are not
        # and a single target does not exist
        expected_original_stale2 = False
        expected_stale2 = True
        (build2.node
                ["stale_alternate_update_highest_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build2.node
                ["stale_alternate_update_highest_target-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build2.node
                ["stale_alternate_update_highest_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build2.node
                ["stale_alternate_update_highest_target-2014-12-05-10-50"]
                ["object"].mtime) = 100
        (build2.node
                ["stale_alternate_update_highest_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build2.node
                ["stale_alternate_update_highest_target-2014-12-05-10-55"]
                ["object"].mtime) = 100
        (build2.node
                ["stale_alternate_update_top_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build2.node
                ["stale_alternate_update_top_target-2014-12-05-10-45"]
                ["object"].mtime) = 150
        (build2.node
                ["stale_alternate_update_top_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build2.node
                ["stale_alternate_update_top_target-2014-12-05-10-50"]
                ["object"].mtime) = 150
        (build2.node
                ["stale_alternate_update_top_target-2014-12-05-10-55"]
                ["object"].exists) = False
        (build2.node
                ["stale_alternate_update_top_target-2014-12-05-10-55"]
                ["object"].mtime) = None
        (build2.node
                ["stale_alternate_update_secondary_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build2.node
                ["stale_alternate_update_secondary_target-2014-12-05-10-45"]
                ["object"].mtime) = 150
        (build2.node
                ["stale_alternate_update_secondary_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build2.node
                ["stale_alternate_update_secondary_target-2014-12-05-10-50"]
                ["object"].mtime) = 150
        (build2.node
                ["stale_alternate_update_secondary_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build2.node
                ["stale_alternate_update_secondary_target-2014-12-05-10-55"]
                ["object"].mtime) = 150
        (build2.node
                ["stale_alternate_update_bottom_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build2.node
                ["stale_alternate_update_bottom_target-2014-12-05-10-45"]
                ["object"].mtime) = 50
        (build2.node
                ["stale_alternate_update_bottom_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build2.node
                ["stale_alternate_update_bottom_target-2014-12-05-10-50"]
                ["object"].mtime) = 50
        (build2.node
                ["stale_alternate_update_bottom_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build2.node
                ["stale_alternate_update_bottom_target-2014-12-05-10-55"]
                ["object"].mtime) = 50

        # All alternate_updates exist and are stale but the targets are not
        # and a single target not form the job doesn't exist
        expected_original_stale3 = False
        expected_stale3 = False
        (build3.node
                ["stale_alternate_update_highest_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build3.node
                ["stale_alternate_update_highest_target-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build3.node
                ["stale_alternate_update_highest_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build3.node
                ["stale_alternate_update_highest_target-2014-12-05-10-50"]
                ["object"].mtime) = 100
        (build3.node
                ["stale_alternate_update_highest_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build3.node
                ["stale_alternate_update_highest_target-2014-12-05-10-55"]
                ["object"].mtime) = 100
        (build3.node
                ["stale_alternate_update_top_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build3.node
                ["stale_alternate_update_top_target-2014-12-05-10-45"]
                ["object"].mtime) = 150
        (build3.node
                ["stale_alternate_update_top_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build3.node
                ["stale_alternate_update_top_target-2014-12-05-10-50"]
                ["object"].mtime) = 150
        (build3.node
                ["stale_alternate_update_top_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build3.node
                ["stale_alternate_update_top_target-2014-12-05-10-55"]
                ["object"].mtime) = 150
        (build3.node
                ["stale_alternate_update_secondary_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build3.node
                ["stale_alternate_update_secondary_target-2014-12-05-10-45"]
                ["object"].mtime) = 150
        (build3.node
                ["stale_alternate_update_secondary_target-2014-12-05-10-50"]
                ["object"].exists) = False
        (build3.node
                ["stale_alternate_update_secondary_target-2014-12-05-10-50"]
                ["object"].mtime) = None
        (build3.node
                ["stale_alternate_update_secondary_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build3.node
                ["stale_alternate_update_secondary_target-2014-12-05-10-55"]
                ["object"].mtime) = 150
        (build3.node
                ["stale_alternate_update_bottom_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build3.node
                ["stale_alternate_update_bottom_target-2014-12-05-10-45"]
                ["object"].mtime) = 50
        (build3.node
                ["stale_alternate_update_bottom_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build3.node
                ["stale_alternate_update_bottom_target-2014-12-05-10-50"]
                ["object"].mtime) = 50
        (build3.node
                ["stale_alternate_update_bottom_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build3.node
                ["stale_alternate_update_bottom_target-2014-12-05-10-55"]
                ["object"].mtime) = 50

        # The job is not stale, missing a target, all alternate_updates exist
        # alternate_update is not stale
        expected_original_stale4 = False
        expected_stale4 = False
        (build4.node
                ["stale_alternate_update_highest_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build4.node
                ["stale_alternate_update_highest_target-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build4.node
                ["stale_alternate_update_highest_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build4.node
                ["stale_alternate_update_highest_target-2014-12-05-10-50"]
                ["object"].mtime) = 100
        (build4.node
                ["stale_alternate_update_highest_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build4.node
                ["stale_alternate_update_highest_target-2014-12-05-10-55"]
                ["object"].mtime) = 100
        (build4.node
                ["stale_alternate_update_top_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build4.node
                ["stale_alternate_update_top_target-2014-12-05-10-45"]
                ["object"].mtime) = 150
        (build4.node
                ["stale_alternate_update_top_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build4.node
                ["stale_alternate_update_top_target-2014-12-05-10-50"]
                ["object"].mtime) = 150
        (build4.node
                ["stale_alternate_update_top_target-2014-12-05-10-55"]
                ["object"].exists) = False
        (build4.node
                ["stale_alternate_update_top_target-2014-12-05-10-55"]
                ["object"].mtime) = None
        (build4.node
                ["stale_alternate_update_secondary_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build4.node
                ["stale_alternate_update_secondary_target-2014-12-05-10-45"]
                ["object"].mtime) = 150
        (build4.node
                ["stale_alternate_update_secondary_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build4.node
                ["stale_alternate_update_secondary_target-2014-12-05-10-50"]
                ["object"].mtime) = 150
        (build4.node
                ["stale_alternate_update_secondary_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build4.node
                ["stale_alternate_update_secondary_target-2014-12-05-10-55"]
                ["object"].mtime) = 150
        (build4.node
                ["stale_alternate_update_bottom_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build4.node
                ["stale_alternate_update_bottom_target-2014-12-05-10-45"]
                ["object"].mtime) = 200
        (build4.node
                ["stale_alternate_update_bottom_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build4.node
                ["stale_alternate_update_bottom_target-2014-12-05-10-50"]
                ["object"].mtime) = 200
        (build4.node
                ["stale_alternate_update_bottom_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build4.node
                ["stale_alternate_update_bottom_target-2014-12-05-10-55"]
                ["object"].mtime) = 200

        # When
        original_stale1 = (build1.node
                ["stale_alternate_update_top_job_2014-12-05-10-45"]
                ["object"].get_stale(build1))
        (build1.node
                ["stale_alternate_update_bottom_job_2014-12-05-10-45"]
                ["object"].get_stale(build1))
        stale1 = (build1.node
                ["stale_alternate_update_top_job_2014-12-05-10-45"]
                ["object"].get_stale(build1))
        original_stale2 = (build2.node
                ["stale_alternate_update_top_job_2014-12-05-10-45"]
                ["object"].get_stale(build2))
        (build2.node
                ["stale_alternate_update_bottom_job_2014-12-05-10-45"]
                ["object"].get_stale(build2))
        stale2 = (build2.node
                ["stale_alternate_update_top_job_2014-12-05-10-45"]
                ["object"].get_stale(build2))
        original_stale3 = (build3.node
                ["stale_alternate_update_top_job_2014-12-05-10-45"]
                ["object"].get_stale(build3))
        (build3.node
                ["stale_alternate_update_bottom_job_2014-12-05-10-45"]
                ["object"].get_stale(build3))
        stale3 = (build3.node
                ["stale_alternate_update_top_job_2014-12-05-10-45"]
                ["object"].get_stale(build3))
        original_stale4 = (build4.node
                ["stale_alternate_update_top_job_2014-12-05-10-45"]
                ["object"].get_stale(build4))
        (build4.node
                ["stale_alternate_update_bottom_job_2014-12-05-10-45"]
                ["object"].get_stale(build4))
        stale4 = (build4.node
                ["stale_alternate_update_top_job_2014-12-05-10-45"]
                ["object"].get_stale(build4))

        # Then
        self.assertEqual(original_stale1, expected_original_stale1)
        self.assertEqual(original_stale2, expected_original_stale2)
        self.assertEqual(original_stale3, expected_original_stale3)
        self.assertEqual(original_stale4, expected_original_stale4)
        self.assertEqual(stale1, expected_stale1)
        self.assertEqual(stale2, expected_stale2)
        self.assertEqual(stale3, expected_stale3)
        self.assertEqual(stale4, expected_stale4)

    @testing.unit
    def test_buildable(self):
        # Given
        jobs1 = [
            BuildableJobTester(),
        ]

        build_context1 = {
            "start_time": arrow.get("2014-12-05T10:50"),
            "end_time": arrow.get("2014-12-05T10:50"),
            "start_job": "buildable_job", # BuildableJobTester,
        }

        build1 = builder.build.Build(jobs1)
        build2 = builder.build.Build(jobs1)
        build3 = builder.build.Build(jobs1)
        build4 = builder.build.Build(jobs1)
        build5 = builder.build.Build(jobs1)
        build6 = builder.build.Build(jobs1)

        build1.construct_build_graph(copy.deepcopy(build_context1))
        build2.construct_build_graph(copy.deepcopy(build_context1))
        build3.construct_build_graph(copy.deepcopy(build_context1))
        build4.construct_build_graph(copy.deepcopy(build_context1))
        build5.construct_build_graph(copy.deepcopy(build_context1))
        build6.construct_build_graph(copy.deepcopy(build_context1))

        # depends 15 minute not met
        expected_buildable1 = False
        (build1.node
                ["buildable_15_minute_target_01-2014-12-05-10-45"]
                ["object"].exists) = False
        (build1.node
                ["buildable_15_minute_target_01-2014-12-05-10-45"]
                ["object"].mtime) = None
        (build1.node
                ["buildable_5_minute_target_01-2014-12-05-10-45"]
                ["object"].exists) = True
        (build1.node
                ["buildable_5_minute_target_01-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build1.node
                ["buildable_5_minute_target_01-2014-12-05-10-50"]
                ["object"].exists) = True
        (build1.node
                ["buildable_5_minute_target_01-2014-12-05-10-50"]
                ["object"].mtime) = 100
        (build1.node
                ["buildable_5_minute_target_01-2014-12-05-10-55"]
                ["object"].exists) = True
        (build1.node
                ["buildable_5_minute_target_01-2014-12-05-10-55"]
                ["object"].mtime) = 100
        (build1.node
                ["buildable_15_minute_target_02-2014-12-05-10-45"]
                ["object"].exists) = True
        (build1.node
                ["buildable_15_minute_target_02-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build1.node
                ["buildable_5_minute_target_02-2014-12-05-10-45"]
                ["object"].exists) = True
        (build1.node
                ["buildable_5_minute_target_02-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build1.node
                ["buildable_5_minute_target_02-2014-12-05-10-50"]
                ["object"].exists) = True
        (build1.node
                ["buildable_5_minute_target_02-2014-12-05-10-50"]
                ["object"].mtime) = 100
        (build1.node
                ["buildable_5_minute_target_02-2014-12-05-10-55"]
                ["object"].exists) = True
        (build1.node
                ["buildable_5_minute_target_02-2014-12-05-10-55"]
                ["object"].mtime) = 100

        # depends 5 minute not met
        expected_buildable2 = False
        (build2.node
                ["buildable_15_minute_target_01-2014-12-05-10-45"]
                ["object"].exists) = True
        (build2.node
                ["buildable_15_minute_target_01-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build2.node
                ["buildable_5_minute_target_01-2014-12-05-10-45"]
                ["object"].exists) = True
        (build2.node
                ["buildable_5_minute_target_01-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build2.node
                ["buildable_5_minute_target_01-2014-12-05-10-50"]
                ["object"].exists) = False
        (build2.node
                ["buildable_5_minute_target_01-2014-12-05-10-50"]
                ["object"].mtime) = None
        (build2.node
                ["buildable_5_minute_target_01-2014-12-05-10-55"]
                ["object"].exists) = True
        (build2.node
                ["buildable_5_minute_target_01-2014-12-05-10-55"]
                ["object"].mtime) = 100
        (build2.node
                ["buildable_15_minute_target_02-2014-12-05-10-45"]
                ["object"].exists) = True
        (build2.node
                ["buildable_15_minute_target_02-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build2.node
                ["buildable_5_minute_target_02-2014-12-05-10-45"]
                ["object"].exists) = True
        (build2.node
                ["buildable_5_minute_target_02-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build2.node
                ["buildable_5_minute_target_02-2014-12-05-10-50"]
                ["object"].exists) = True
        (build2.node
                ["buildable_5_minute_target_02-2014-12-05-10-50"]
                ["object"].mtime) = 100
        (build2.node
                ["buildable_5_minute_target_02-2014-12-05-10-55"]
                ["object"].exists) = True
        (build2.node
                ["buildable_5_minute_target_02-2014-12-05-10-55"]
                ["object"].mtime) = 100

        # depends one or more 15 not met
        expected_buildable3 = False
        (build3.node
                ["buildable_15_minute_target_01-2014-12-05-10-45"]
                ["object"].exists) = True
        (build3.node
                ["buildable_15_minute_target_01-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build3.node
                ["buildable_5_minute_target_01-2014-12-05-10-45"]
                ["object"].exists) = True
        (build3.node
                ["buildable_5_minute_target_01-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build3.node
                ["buildable_5_minute_target_01-2014-12-05-10-50"]
                ["object"].exists) = True
        (build3.node
                ["buildable_5_minute_target_01-2014-12-05-10-50"]
                ["object"].mtime) = 100
        (build3.node
                ["buildable_5_minute_target_01-2014-12-05-10-55"]
                ["object"].exists) = True
        (build3.node
                ["buildable_5_minute_target_01-2014-12-05-10-55"]
                ["object"].mtime) = 100
        (build3.node
                ["buildable_15_minute_target_02-2014-12-05-10-45"]
                ["object"].exists) = False
        (build3.node
                ["buildable_15_minute_target_02-2014-12-05-10-45"]
                ["object"].mtime) = None
        (build3.node
                ["buildable_5_minute_target_02-2014-12-05-10-45"]
                ["object"].exists) = True
        (build3.node
                ["buildable_5_minute_target_02-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build3.node
                ["buildable_5_minute_target_02-2014-12-05-10-50"]
                ["object"].exists) = True
        (build3.node
                ["buildable_5_minute_target_02-2014-12-05-10-50"]
                ["object"].mtime) = 100
        (build3.node
                ["buildable_5_minute_target_02-2014-12-05-10-55"]
                ["object"].exists) = True
        (build3.node
                ["buildable_5_minute_target_02-2014-12-05-10-55"]
                ["object"].mtime) = 100

        # depends one or more 5 not met
        expected_buildable4 = False
        (build4.node
                ["buildable_15_minute_target_01-2014-12-05-10-45"]
                ["object"].exists) = True
        (build4.node
                ["buildable_15_minute_target_01-2014-12-05-10-45"]
                ["object"].mtime) = False
        (build4.node
                ["buildable_5_minute_target_01-2014-12-05-10-45"]
                ["object"].exists) = True
        (build4.node
                ["buildable_5_minute_target_01-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build4.node
                ["buildable_5_minute_target_01-2014-12-05-10-50"]
                ["object"].exists) = True
        (build4.node
                ["buildable_5_minute_target_01-2014-12-05-10-50"]
                ["object"].mtime) = 100
        (build4.node
                ["buildable_5_minute_target_01-2014-12-05-10-55"]
                ["object"].exists) = True
        (build4.node
                ["buildable_5_minute_target_01-2014-12-05-10-55"]
                ["object"].mtime) = 100
        (build4.node
                ["buildable_15_minute_target_02-2014-12-05-10-45"]
                ["object"].exists) = True
        (build4.node
                ["buildable_15_minute_target_02-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build4.node
                ["buildable_5_minute_target_02-2014-12-05-10-45"]
                ["object"].exists) = False
        (build4.node
                ["buildable_5_minute_target_02-2014-12-05-10-45"]
                ["object"].mtime) = None
        (build4.node
                ["buildable_5_minute_target_02-2014-12-05-10-50"]
                ["object"].exists) = False
        (build4.node
                ["buildable_5_minute_target_02-2014-12-05-10-50"]
                ["object"].mtime) = None
        (build4.node
                ["buildable_5_minute_target_02-2014-12-05-10-55"]
                ["object"].exists) = False
        (build4.node
                ["buildable_5_minute_target_02-2014-12-05-10-55"]
                ["object"].mtime) = None

        # all not met
        expected_buildable5 = False
        (build5.node
                ["buildable_15_minute_target_01-2014-12-05-10-45"]
                ["object"].exists) = False
        (build5.node
                ["buildable_15_minute_target_01-2014-12-05-10-45"]
                ["object"].mtime) = None
        (build5.node
                ["buildable_5_minute_target_01-2014-12-05-10-45"]
                ["object"].exists) = True
        (build5.node
                ["buildable_5_minute_target_01-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build5.node
                ["buildable_5_minute_target_01-2014-12-05-10-50"]
                ["object"].exists) = False
        (build5.node
                ["buildable_5_minute_target_01-2014-12-05-10-50"]
                ["object"].mtime) = None
        (build5.node
                ["buildable_5_minute_target_01-2014-12-05-10-55"]
                ["object"].exists) = True
        (build5.node
                ["buildable_5_minute_target_01-2014-12-05-10-55"]
                ["object"].mtime) = 100
        (build5.node
                ["buildable_15_minute_target_02-2014-12-05-10-45"]
                ["object"].exists) = False
        (build5.node
                ["buildable_15_minute_target_02-2014-12-05-10-45"]
                ["object"].mtime) = None
        (build5.node
                ["buildable_5_minute_target_02-2014-12-05-10-45"]
                ["object"].exists) = False
        (build5.node
                ["buildable_5_minute_target_02-2014-12-05-10-45"]
                ["object"].mtime) = None
        (build5.node
                ["buildable_5_minute_target_02-2014-12-05-10-50"]
                ["object"].exists) = False
        (build5.node
                ["buildable_5_minute_target_02-2014-12-05-10-50"]
                ["object"].mtime) = None
        (build5.node
                ["buildable_5_minute_target_02-2014-12-05-10-55"]
                ["object"].exists) = False
        (build5.node
                ["buildable_5_minute_target_02-2014-12-05-10-55"]
                ["object"].mtime) = None

        # all met
        expected_buildable6 = True
        (build6.node
                ["buildable_15_minute_target_01-2014-12-05-10-45"]
                ["object"].exists) = 100
        (build6.node
                ["buildable_15_minute_target_01-2014-12-05-10-45"]
                ["object"].mtime) = True
        (build6.node
                ["buildable_5_minute_target_01-2014-12-05-10-45"]
                ["object"].exists) = True
        (build6.node
                ["buildable_5_minute_target_01-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build6.node
                ["buildable_5_minute_target_01-2014-12-05-10-50"]
                ["object"].exists) = True
        (build6.node
                ["buildable_5_minute_target_01-2014-12-05-10-50"]
                ["object"].mtime) = 100
        (build6.node
                ["buildable_5_minute_target_01-2014-12-05-10-55"]
                ["object"].exists) = True
        (build6.node
                ["buildable_5_minute_target_01-2014-12-05-10-55"]
                ["object"].mtime) = 100
        (build6.node
                ["buildable_15_minute_target_02-2014-12-05-10-45"]
                ["object"].exists) = True
        (build6.node
                ["buildable_15_minute_target_02-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build6.node
                ["buildable_5_minute_target_02-2014-12-05-10-45"]
                ["object"].exists) = False
        (build6.node
                ["buildable_5_minute_target_02-2014-12-05-10-45"]
                ["object"].mtime) = None
        (build6.node
                ["buildable_5_minute_target_02-2014-12-05-10-50"]
                ["object"].exists) = False
        (build6.node
                ["buildable_5_minute_target_02-2014-12-05-10-50"]
                ["object"].mtime) = None
        (build6.node
                ["buildable_5_minute_target_02-2014-12-05-10-55"]
                ["object"].exists) = True
        (build6.node
                ["buildable_5_minute_target_02-2014-12-05-10-55"]
                ["object"].mtime) = 100

        # When
        buildable1 = (build1.node
                ["buildable_job_2014-12-05-10-45"]
                ["object"].get_buildable(build1))
        buildable2 = (build2.node
                ["buildable_job_2014-12-05-10-45"]
                ["object"].get_buildable(build2))
        buildable3 = (build3.node
                ["buildable_job_2014-12-05-10-45"]
                ["object"].get_buildable(build3))
        buildable4 = (build4.node
                ["buildable_job_2014-12-05-10-45"]
                ["object"].get_buildable(build4))
        buildable5 = (build5.node
                ["buildable_job_2014-12-05-10-45"]
                ["object"].get_buildable(build5))
        buildable6 = (build6.node
                ["buildable_job_2014-12-05-10-45"]
                ["object"].get_buildable(build6))

        # Then
        self.assertEqual(buildable1, expected_buildable1)
        self.assertEqual(buildable2, expected_buildable2)
        self.assertEqual(buildable3, expected_buildable3)
        self.assertEqual(buildable4, expected_buildable4)
        self.assertEqual(buildable5, expected_buildable5)
        self.assertEqual(buildable6, expected_buildable6)

    @testing.unit
    def test_past_cache_time(self):
        # Given
        current_time = 400

        build_context1 = {
            "start_time": arrow.get("2014-12-05T10:55"),
            "end_time": arrow.get("2014-12-05T10:55"),
            "start_job": "past_cache_time_job", # PastCacheTimeJobTester,
        }

        jobs1 = [
            PastCacheTimeJobTester(),
        ]

        build1 = builder.build.Build(jobs1)
        build2 = builder.build.Build(jobs1)
        build3 = builder.build.Build(jobs1)

        build1.construct_build_graph(copy.deepcopy(build_context1))
        build2.construct_build_graph(copy.deepcopy(build_context1))
        build3.construct_build_graph(copy.deepcopy(build_context1))

        # a target doesn't exist
        expected_past_cache_time1 = True
        (build1.node
                ["past_cache_time_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build1.node
                ["past_cache_time_target-2014-12-05-10-45"]
                ["object"].mtime) = 400
        (build1.node
                ["past_cache_time_target-2014-12-05-10-50"]
                ["object"].exists) = False
        (build1.node
                ["past_cache_time_target-2014-12-05-10-50"]
                ["object"].mtime) = None
        (build1.node
                ["past_cache_time_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build1.node
                ["past_cache_time_target-2014-12-05-10-55"]
                ["object"].mtime) = 400

        # all targets are within the allowed time
        expected_past_cache_time2 = False
        (build2.node
                ["past_cache_time_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build2.node
                ["past_cache_time_target-2014-12-05-10-45"]
                ["object"].mtime) = 400
        (build2.node
                ["past_cache_time_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build2.node
                ["past_cache_time_target-2014-12-05-10-50"]
                ["object"].mtime) = 400
        (build2.node
                ["past_cache_time_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build2.node
                ["past_cache_time_target-2014-12-05-10-55"]
                ["object"].mtime) = 400

        # no target is within the allowed time
        expected_past_cache_time3 = True
        (build3.node
                ["past_cache_time_target-2014-12-05-10-45"]
                ["object"].exists) = True
        (build3.node
                ["past_cache_time_target-2014-12-05-10-45"]
                ["object"].mtime) = 50
        (build3.node
                ["past_cache_time_target-2014-12-05-10-50"]
                ["object"].exists) = True
        (build3.node
                ["past_cache_time_target-2014-12-05-10-50"]
                ["object"].mtime) = 50
        (build3.node
                ["past_cache_time_target-2014-12-05-10-55"]
                ["object"].exists) = True
        (build3.node
                ["past_cache_time_target-2014-12-05-10-55"]
                ["object"].mtime) = 50

        old_arrow_get = copy.deepcopy(arrow.get)
        def new_arrow_get(*args, **kwargs):
            """This wraps the original arrow get so we can override only
            arrow get with no args
            """
            if not args and not kwargs:
                return arrow.get(current_time)
            else:
                return old_arrow_get(*args, **kwargs)

        mock_arrow_get = mock.Mock(side_effect=new_arrow_get)

        # When
        with mock.patch("arrow.get", mock_arrow_get):
            past_cache_time1 = (build1.node
                    ["past_cache_time_job_2014-12-05-10-45"]
                    ["object"].past_cache_time(build1))
            past_cache_time2 = (build2.node
                    ["past_cache_time_job_2014-12-05-10-45"]
                    ["object"].past_cache_time(build2))
            past_cache_time3 = (build3.node
                    ["past_cache_time_job_2014-12-05-10-45"]
                    ["object"].past_cache_time(build3))

        # Then
        self.assertEqual(past_cache_time1, expected_past_cache_time1)
        self.assertEqual(past_cache_time2, expected_past_cache_time2)
        self.assertEqual(past_cache_time3, expected_past_cache_time3)

    @testing.unit
    def test_all_dependencies(self):
        # Given
        jobs1 = [
            AllDependenciesJobTester(),
        ]

        build_context1 = {
            "start_time": "2014-12-05T10:55",
            "end_time": "2014-12-05T10:55",
            "start_job": "all_dependencies_job", # AllDependenciesJobTester,
        }

        build1 = builder.build.Build(jobs1)
        build2 = builder.build.Build(jobs1)
        build3 = builder.build.Build(jobs1)
        build4 = builder.build.Build(jobs1)

        build1.construct_build_graph(copy.deepcopy(build_context1))
        build2.construct_build_graph(copy.deepcopy(build_context1))
        build3.construct_build_graph(copy.deepcopy(build_context1))
        build4.construct_build_graph(copy.deepcopy(build_context1))

        # all dependencies
        expected_all_dependencies1 = True
        (build1.node
                ["all_dependencies_target_01-2014-12-05-10-45"]
                ["object"].exists) = True
        (build1.node
                ["all_dependencies_target_01-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build1.node
                ["all_dependencies_target_01-2014-12-05-10-50"]
                ["object"].exists) = True
        (build1.node
                ["all_dependencies_target_01-2014-12-05-10-50"]
                ["object"].mtime) = 100
        (build1.node
                ["all_dependencies_target_01-2014-12-05-10-55"]
                ["object"].exists) = True
        (build1.node
                ["all_dependencies_target_01-2014-12-05-10-55"]
                ["object"].mtime) = 100
        (build1.node
                ["all_dependencies_target_02-2014-12-05-10-45"]
                ["object"].exists) = True
        (build1.node
                ["all_dependencies_target_02-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build1.node
                ["all_dependencies_target_02-2014-12-05-10-50"]
                ["object"].exists) = True
        (build1.node
                ["all_dependencies_target_02-2014-12-05-10-50"]
                ["object"].mtime) = 100
        (build1.node
                ["all_dependencies_target_02-2014-12-05-10-55"]
                ["object"].exists) = True
        (build1.node
                ["all_dependencies_target_02-2014-12-05-10-55"]
                ["object"].mtime) = 100
        # 01 missing one target
        expected_all_dependencies2 = False
        (build2.node
                ["all_dependencies_target_01-2014-12-05-10-45"]
                ["object"].exists) = True
        (build2.node
                ["all_dependencies_target_01-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build2.node
                ["all_dependencies_target_01-2014-12-05-10-50"]
                ["object"].exists) = False
        (build2.node
                ["all_dependencies_target_01-2014-12-05-10-50"]
                ["object"].mtime) = None
        (build2.node
                ["all_dependencies_target_01-2014-12-05-10-55"]
                ["object"].exists) = True
        (build2.node
                ["all_dependencies_target_01-2014-12-05-10-55"]
                ["object"].mtime) = 100
        (build2.node
                ["all_dependencies_target_02-2014-12-05-10-45"]
                ["object"].exists) = True
        (build2.node
                ["all_dependencies_target_02-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build2.node
                ["all_dependencies_target_02-2014-12-05-10-50"]
                ["object"].exists) = True
        (build2.node
                ["all_dependencies_target_02-2014-12-05-10-50"]
                ["object"].mtime) = 100
        (build2.node
                ["all_dependencies_target_02-2014-12-05-10-55"]
                ["object"].exists) = True
        (build2.node
                ["all_dependencies_target_02-2014-12-05-10-55"]
                ["object"].mtime) = 100
        # 02 missing one target
        expected_all_dependencies3 = True
        (build3.node
                ["all_dependencies_target_01-2014-12-05-10-45"]
                ["object"].exists) = True
        (build3.node
                ["all_dependencies_target_01-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build3.node
                ["all_dependencies_target_01-2014-12-05-10-50"]
                ["object"].exists) = True
        (build3.node
                ["all_dependencies_target_01-2014-12-05-10-50"]
                ["object"].mtime) = 100
        (build3.node
                ["all_dependencies_target_01-2014-12-05-10-55"]
                ["object"].exists) = True
        (build3.node
                ["all_dependencies_target_01-2014-12-05-10-55"]
                ["object"].mtime) = 100
        (build3.node
                ["all_dependencies_target_02-2014-12-05-10-45"]
                ["object"].exists) = True
        (build3.node
                ["all_dependencies_target_02-2014-12-05-10-45"]
                ["object"].mtime) = 100
        (build3.node
                ["all_dependencies_target_02-2014-12-05-10-50"]
                ["object"].exists) = True
        (build3.node
                ["all_dependencies_target_02-2014-12-05-10-50"]
                ["object"].mtime) = 100
        (build3.node
                ["all_dependencies_target_02-2014-12-05-10-55"]
                ["object"].exists) = True
        (build3.node
                ["all_dependencies_target_02-2014-12-05-10-55"]
                ["object"].mtime) = 100
        # all deps missing
        expected_all_dependencies4 = False
        (build4.node
                ["all_dependencies_target_01-2014-12-05-10-45"]
                ["object"].exists) = False
        (build4.node
                ["all_dependencies_target_01-2014-12-05-10-45"]
                ["object"].mtime) = None
        (build4.node
                ["all_dependencies_target_01-2014-12-05-10-50"]
                ["object"].exists) = False
        (build4.node
                ["all_dependencies_target_01-2014-12-05-10-50"]
                ["object"].mtime) = None
        (build4.node
                ["all_dependencies_target_01-2014-12-05-10-55"]
                ["object"].exists) = False
        (build4.node
                ["all_dependencies_target_01-2014-12-05-10-55"]
                ["object"].mtime) = None
        (build4.node
                ["all_dependencies_target_02-2014-12-05-10-45"]
                ["object"].exists) = False
        (build4.node
                ["all_dependencies_target_02-2014-12-05-10-45"]
                ["object"].mtime) = None
        (build4.node
                ["all_dependencies_target_02-2014-12-05-10-50"]
                ["object"].exists) = False
        (build4.node
                ["all_dependencies_target_02-2014-12-05-10-50"]
                ["object"].mtime) = None
        (build4.node
                ["all_dependencies_target_02-2014-12-05-10-55"]
                ["object"].exists) = False
        (build4.node
                ["all_dependencies_target_02-2014-12-05-10-55"]
                ["object"].mtime) = None

        # When
        all_dependencies1 = (build1.node
                ["all_dependencies_job_2014-12-05-10-45"]
                ["object"].all_dependencies(build1))
        all_dependencies2 = (build1.node
                ["all_dependencies_job_2014-12-05-10-45"]
                ["object"].all_dependencies(build2))
        all_dependencies3 = (build1.node
                ["all_dependencies_job_2014-12-05-10-45"]
                ["object"].all_dependencies(build3))
        all_dependencies4 = (build1.node
                ["all_dependencies_job_2014-12-05-10-45"]
                ["object"].all_dependencies(build4))

        # Then
        self.assertEqual(all_dependencies1, expected_all_dependencies1)
        self.assertEqual(all_dependencies2, expected_all_dependencies2)
        self.assertEqual(all_dependencies3, expected_all_dependencies3)
        self.assertEqual(all_dependencies4, expected_all_dependencies4)

    @testing.unit
    def test_should_run_logic(self):
        # Given
        job1 = ShouldRunLogicJobTester().expand({})[0]
        job2 = ShouldRunLogicJobTester().expand({})[0]
        job3 = ShouldRunLogicJobTester().expand({})[0]
        job4 = ShouldRunLogicJobTester().expand({})[0]
        job5 = ShouldRunLogicJobTester().expand({})[0]
        job6 = ShouldRunLogicJobTester().expand({})[0]
        job7 = ShouldRunCacheLogicJobTester().expand({})[0]
        job8 = ShouldRunCacheLogicJobTester().expand({})[0]
        job9 = ShouldRunCacheLogicJobTester().expand({})[0]
        job10 = ShouldRunCacheLogicJobTester().expand({})[0]
        job11 = ShouldRunCacheLogicJobTester().expand({})[0]
        job12 = ShouldRunCacheLogicJobTester().expand({})[0]
        job13 = ShouldRunLogicJobTester().expand({})[0]
        job14 = ShouldRunCacheLogicJobTester().expand({})[0]

        graph1 = networkx.DiGraph()
        graph1.add_node("unique_id1", object=job1)
        graph2 = networkx.DiGraph()
        graph2.add_node("unique_id2", object=job2)
        graph3 = networkx.DiGraph()
        graph3.add_node("unique_id3", object=job3)
        graph4 = networkx.DiGraph()
        graph4.add_node("unique_id4", object=job4)
        graph5 = networkx.DiGraph()
        graph5.add_node("unique_id5", object=job5)
        graph6 = networkx.DiGraph()
        graph6.add_node("unique_id6", object=job6)
        graph7 = networkx.DiGraph()
        graph7.add_node("unique_id7", object=job7)
        graph8 = networkx.DiGraph()
        graph8.add_node("unique_id8", object=job8)
        graph9 = networkx.DiGraph()
        graph9.add_node("unique_id9", object=job9)
        graph10 = networkx.DiGraph()
        graph10.add_node("unique_id10", object=job10)
        graph11 = networkx.DiGraph()
        graph11.add_node("unique_id11", object=job11)
        graph12 = networkx.DiGraph()
        graph12.add_node("unique_id12", object=job12)
        graph13 = networkx.DiGraph()
        graph13.add_node("unique_id13", object=job13)
        graph14 = networkx.DiGraph()
        graph14.add_node("unique_id14", object=job14)

        # all true
        expected_should_run1 = True
        graph1.node["unique_id1"]["object"].stale = True
        graph1.node["unique_id1"]["object"].buildable = True
        graph1.node["unique_id1"]["object"].past_curfew = (
                mock.Mock(return_value=True))
        graph1.node["unique_id1"]["object"].all_dependencies = (
                mock.Mock(return_value=True))
        graph1.node["unique_id1"]["object"].get_parents_should_not_run = (
                mock.Mock(return_value=True))
        # not stale everything else true
        expected_should_run2 = False
        graph2.node["unique_id2"]["object"].stale = False
        graph2.node["unique_id2"]["object"].buildable = True
        graph2.node["unique_id2"]["object"].past_curfew = (
                mock.Mock(return_value=True))
        graph2.node["unique_id2"]["object"].all_dependencies = (
                mock.Mock(return_value=True))
        graph2.node["unique_id2"]["object"].get_parents_should_not_run = (
                mock.Mock(return_value=True))
        # not buildable everything else true
        expected_should_run3 = False
        graph3.node["unique_id3"]["object"].stale = True
        graph3.node["unique_id3"]["object"].buildable = False
        graph3.node["unique_id3"]["object"].past_curfew = (
                mock.Mock(return_value=True))
        graph3.node["unique_id3"]["object"].all_dependencies = (
                mock.Mock(return_value=True))
        graph3.node["unique_id3"]["object"].get_parents_should_not_run = (
                mock.Mock(return_value=True))
        # not past curfew everything else true
        expected_should_run4 = True
        graph4.node["unique_id4"]["object"].stale = True
        graph4.node["unique_id4"]["object"].buildable = True
        graph4.node["unique_id4"]["object"].past_curfew = (
                mock.Mock(return_value=False))
        graph4.node["unique_id4"]["object"].all_dependencies = (
                mock.Mock(return_value=True))
        graph4.node["unique_id4"]["object"].get_parents_should_not_run = (
                mock.Mock(return_value=True))
        # not all dependencies everything else true
        expected_should_run5 = True
        graph5.node["unique_id5"]["object"].stale = True
        graph5.node["unique_id5"]["object"].buildable = True
        graph5.node["unique_id5"]["object"].past_curfew = (
                mock.Mock(return_value=True))
        graph5.node["unique_id5"]["object"].all_dependencies = (
                mock.Mock(return_value=False))
        graph5.node["unique_id5"]["object"].get_parents_should_not_run = (
                mock.Mock(return_value=True))
        # parents should run, everything else is true
        expected_should_run6 = False
        graph6.node["unique_id6"]["object"].stale = True
        graph6.node["unique_id6"]["object"].buildable = True
        graph6.node["unique_id6"]["object"].past_curfew = (
                mock.Mock(return_value=True))
        graph6.node["unique_id6"]["object"].all_dependencies = (
                mock.Mock(return_value=True))
        graph6.node["unique_id6"]["object"].get_parents_should_not_run = (
                mock.Mock(return_value=False))
        # cache not past curfew
        expected_should_run7 = True
        graph7.node["unique_id7"]["object"].stale = True
        graph7.node["unique_id7"]["object"].buildable = True
        graph7.node["unique_id7"]["object"].past_curfew = (
                mock.Mock(return_value=False))
        graph7.node["unique_id7"]["object"].all_dependencies = (
                mock.Mock(return_value=True))
        graph7.node["unique_id7"]["object"].past_cache_time = (
                mock.Mock(return_value=True))
        graph7.node["unique_id7"]["object"].get_parents_should_not_run = (
                mock.Mock(return_value=True))
        # cache not all dependencies
        expected_should_run8 = True
        graph8.node["unique_id8"]["object"].stale = True
        graph8.node["unique_id8"]["object"].buildable = True
        graph8.node["unique_id8"]["object"].past_curfew = (
                mock.Mock(return_value=True))
        graph8.node["unique_id8"]["object"].all_dependencies = (
                mock.Mock(return_value=False))
        graph8.node["unique_id8"]["object"].past_cache_time = (
                mock.Mock(return_value=True))
        graph8.node["unique_id8"]["object"].get_parents_should_not_run = (
                mock.Mock(return_value=True))
        # cache not stale
        expected_should_run9 = False
        graph9.node["unique_id9"]["object"].stale = False
        graph9.node["unique_id9"]["object"].buildable = True
        graph9.node["unique_id9"]["object"].past_curfew = (
                mock.Mock(return_value=True))
        graph9.node["unique_id9"]["object"].all_dependencies = (
                mock.Mock(return_value=True))
        graph9.node["unique_id9"]["object"].past_cache_time = (
                mock.Mock(return_value=True))
        graph9.node["unique_id9"]["object"].get_parents_should_not_run = (
                mock.Mock(return_value=True))
        # cache not buildable
        expected_should_run10 = False
        graph10.node["unique_id10"]["object"].stale = True
        graph10.node["unique_id10"]["object"].buildable = False
        graph10.node["unique_id10"]["object"].past_curfew = (
                mock.Mock(return_value=True))
        graph10.node["unique_id10"]["object"].all_dependencies = (
                mock.Mock(return_value=True))
        graph10.node["unique_id10"]["object"].past_cache_time = (
                mock.Mock(return_value=True))
        graph10.node["unique_id10"]["object"].get_parents_should_not_run = (
                mock.Mock(return_value=True))
        # all true not past cache
        expected_should_run11 = False
        graph11.node["unique_id11"]["object"].stale = False
        graph11.node["unique_id11"]["object"].buildable = True
        graph11.node["unique_id11"]["object"].past_curfew = (
                mock.Mock(return_value=True))
        graph11.node["unique_id11"]["object"].all_dependencies = (
                mock.Mock(return_value=True))
        graph11.node["unique_id11"]["object"].past_cache_time = (
                mock.Mock(return_value=False))
        graph11.node["unique_id11"]["object"].get_parents_should_not_run = (
                mock.Mock(return_value=True))
        # parents should run
        expected_should_run12 = False
        graph12.node["unique_id12"]["object"].stale = True
        graph12.node["unique_id12"]["object"].buildable = True
        graph12.node["unique_id12"]["object"].past_curfew = (
                mock.Mock(return_value=True))
        graph12.node["unique_id12"]["object"].all_dependencies = (
                mock.Mock(return_value=True))
        graph12.node["unique_id12"]["object"].past_cache_time = (
                mock.Mock(return_value=True))
        graph12.node["unique_id12"]["object"].get_parents_should_not_run = (
                mock.Mock(return_value=False))
        # not past curfew and not all dependencies
        expected_should_run13 = False
        graph13.node["unique_id13"]["object"].stale = True
        graph13.node["unique_id13"]["object"].buildable = True
        graph13.node["unique_id13"]["object"].past_curfew = (
                mock.Mock(return_value=False))
        graph13.node["unique_id13"]["object"].all_dependencies = (
                mock.Mock(return_value=False))
        graph13.node["unique_id13"]["object"].get_parents_should_not_run = (
                mock.Mock(return_value=True))
        # not past curfew and not all dependencies has cache_time
        expected_should_run14 = True
        graph14.node["unique_id14"]["object"].stale = True
        graph14.node["unique_id14"]["object"].buildable = True
        graph14.node["unique_id14"]["object"].past_curfew = (
               mock.Mock(return_value=False))
        graph14.node["unique_id14"]["object"].all_dependencies = (
                mock.Mock(return_value=False))
        graph14.node["unique_id14"]["object"].get_parents_should_not_run = (
                mock.Mock(return_value=True))

        # When
        should_run1 = graph1.node["unique_id1"]["object"].get_should_run(
                graph1)
        should_run2 = graph2.node["unique_id2"]["object"].get_should_run(
                graph2)
        should_run3 = graph3.node["unique_id3"]["object"].get_should_run(
                graph3)
        should_run4 = graph4.node["unique_id4"]["object"].get_should_run(
                graph4)
        should_run5 = graph5.node["unique_id5"]["object"].get_should_run(
                graph5)
        should_run6 = graph6.node["unique_id6"]["object"].get_should_run(
                graph6)
        should_run7 = graph7.node["unique_id7"]["object"].get_should_run(
                graph7)
        should_run8 = graph8.node["unique_id8"]["object"].get_should_run(
                graph8)
        should_run9 = graph9.node["unique_id9"]["object"].get_should_run(
                graph9)
        should_run10 = graph10.node["unique_id10"]["object"].get_should_run(
                graph10)
        should_run11 = graph11.node["unique_id11"]["object"].get_should_run(
                graph11)
        should_run12 = graph12.node["unique_id12"]["object"].get_should_run(
                graph12)
        should_run13 = graph13.node["unique_id13"]["object"].get_should_run(
                graph13)
        should_run14 = graph14.node["unique_id14"]["object"].get_should_run(
                graph14)

        # Then
        self.assertEqual(should_run1, expected_should_run1)
        self.assertEqual(should_run2, expected_should_run2)
        self.assertEqual(should_run3, expected_should_run3)
        self.assertEqual(should_run4, expected_should_run4)
        self.assertEqual(should_run5, expected_should_run5)
        self.assertEqual(should_run6, expected_should_run6)
        self.assertEqual(should_run7, expected_should_run7)
        self.assertEqual(should_run8, expected_should_run8)
        self.assertEqual(should_run9, expected_should_run9)
        self.assertEqual(should_run10, expected_should_run10)
        self.assertEqual(should_run11, expected_should_run11)
        self.assertEqual(should_run12, expected_should_run12)
        self.assertEqual(should_run13, expected_should_run13)
        self.assertEqual(should_run14, expected_should_run14)

    @testing.unit
    def test_past_curfew(self):
        # Given
        job1 = PastCurfewJobTester().expand({})[0]
        job2 = PastCurfewTimestampJobTester().expand(
                {
                    "start_time": arrow.get(400),
                    "end_time": arrow.get(400),
                })[0]
        job3 = PastCurfewTimestampJobTester().expand(
                {
                    "start_time": arrow.get(100),
                    "end_time": arrow.get(100),
                })[0]

        current_time = 1000

        expected_past_curfew1 = True
        expected_past_curfew2 = False
        expected_past_curfew3 = True

        old_arrow_get = copy.deepcopy(arrow.get)
        def new_arrow_get(*args, **kwargs):
            """This wraps the original arrow get so we can override only
            arrow get with no args
            """
            if not args and not kwargs:
                return arrow.get(current_time)
            else:
                return old_arrow_get(*args, **kwargs)

        # When
        with mock.patch("arrow.get", new_arrow_get):
            past_curfew1 = job1.past_curfew()
            past_curfew2 = job2.past_curfew()
            past_curfew3 = job3.past_curfew()

        # Then
        self.assertEqual(past_curfew1, expected_past_curfew1)
        self.assertEqual(past_curfew2, expected_past_curfew2)
        self.assertEqual(past_curfew3, expected_past_curfew3)

    @testing.unit
    def test_should_run_recurse(self):
        # Given
        jobs1 = [
            ShouldRunRecurseJob01Tester(),
            ShouldRunRecurseJob02Tester(),
            ShouldRunRecurseJob03Tester(),
            ShouldRunRecurseJob04Tester(),
            ShouldRunRecurseJob05Tester(),
            ShouldRunRecurseJob06Tester(),
            ShouldRunRecurseJob07Tester(),
            ShouldRunRecurseJob08Tester(),
            ShouldRunRecurseJob09Tester(),
            ShouldRunRecurseJob10Tester(),
        ]

        build_context1 = {
            "start_time": arrow.get("2014-12-05T10:55"),
            "end_time": arrow.get("2014-12-05T10:55"),
            "start_job": "should_run_recurse_job_10", # ShouldRunRecurseJob10Tester,
        }

        build1 = builder.build.Build(jobs1)
        build2 = builder.build.Build(jobs1)
        build3 = builder.build.Build(jobs1)
        build4 = builder.build.Build(jobs1)
        build5 = builder.build.Build(jobs1)
        build6 = builder.build.Build(jobs1)
        build7 = builder.build.Build(jobs1)
        build8 = builder.build.Build(jobs1)
        build9 = builder.build.Build(jobs1)
        build10 = builder.build.Build(jobs1)

        build1.construct_build_graph(copy.deepcopy(build_context1))
        build2.construct_build_graph(copy.deepcopy(build_context1))
        build3.construct_build_graph(copy.deepcopy(build_context1))
        build4.construct_build_graph(copy.deepcopy(build_context1))
        build5.construct_build_graph(copy.deepcopy(build_context1))
        build6.construct_build_graph(copy.deepcopy(build_context1))
        build7.construct_build_graph(copy.deepcopy(build_context1))
        build8.construct_build_graph(copy.deepcopy(build_context1))
        build9.construct_build_graph(copy.deepcopy(build_context1))
        build10.construct_build_graph(copy.deepcopy(build_context1))

        expected_parents_should_not_run1 = True
        expected_parents_should_not_run2 = True
        expected_parents_should_not_run3 = False
        expected_parents_should_not_run4 = False
        expected_parents_should_not_run5 = True
        expected_parents_should_not_run6 = True
        expected_parents_should_not_run7 = False
        expected_parents_should_not_run8 = False
        expected_parents_should_not_run9 = True
        expected_parents_should_not_run10 = True

        # When
        parents_should_not_run1 = (build1.node
                ["should_run_recurse_job_01"]
                ["object"].get_parents_should_not_run(
                        build1, False))
        parents_should_not_run2 = (build2.node
                ["should_run_recurse_job_02"]
                ["object"].get_parents_should_not_run(
                        build2, False))
        parents_should_not_run3 = (build3.node
                ["should_run_recurse_job_03"]
                ["object"].get_parents_should_not_run(
                        build3, False))
        parents_should_not_run4 = (build4.node
                ["should_run_recurse_job_04"]
                ["object"].get_parents_should_not_run(
                        build4, False))
        parents_should_not_run5 = (build5.node
                ["should_run_recurse_job_05"]
                ["object"].get_parents_should_not_run(
                        build5, True))
        parents_should_not_run6 = (build6.node
                ["should_run_recurse_job_06"]
                ["object"].get_parents_should_not_run(
                        build6, True))
        parents_should_not_run7 = (build7.node
                ["should_run_recurse_job_07"]
                ["object"].get_parents_should_not_run(
                        build7, True))
        parents_should_not_run8 = (build8.node
                ["should_run_recurse_job_08"]
                ["object"].get_parents_should_not_run(
                        build8, True))
        parents_should_not_run9 = (build9.node
                ["should_run_recurse_job_09"]
                ["object"].get_parents_should_not_run(
                        build9, False))
        parents_should_not_run10 = (build10.node
                ["should_run_recurse_job_10"]
                ["object"].get_parents_should_not_run(
                        build10, False))

        # Then
        self.assertEqual(parents_should_not_run1,
                         expected_parents_should_not_run1)
        self.assertEqual(parents_should_not_run2,
                         expected_parents_should_not_run2)
        self.assertEqual(parents_should_not_run3,
                         expected_parents_should_not_run3)
        self.assertEqual(parents_should_not_run4,
                         expected_parents_should_not_run4)
        self.assertEqual(parents_should_not_run5,
                         expected_parents_should_not_run5)
        self.assertEqual(parents_should_not_run6,
                         expected_parents_should_not_run6)
        self.assertEqual(parents_should_not_run7,
                         expected_parents_should_not_run7)
        self.assertEqual(parents_should_not_run8,
                         expected_parents_should_not_run8)
        self.assertEqual(parents_should_not_run9,
                         expected_parents_should_not_run9)
        self.assertEqual(parents_should_not_run10,
                         expected_parents_should_not_run10)

    @testing.unit
    def test_get_starting_jobs(self):
        # given
        jobs = [GetStartingJobs01Tester(),
                GetStartingJobs02Tester(),
                GetStartingJobs03Tester(),
                GetStartingJobs04Tester()]

        build1 = builder.build.Build(jobs)

        build_context = {}
        for job in jobs:
            build_context["start_job"] = job.unexpanded_id
            build1.construct_build_graph(copy.deepcopy(build_context))

        expected_starting_jobs = [
                (build1.node
                        ["get_starting_jobs_01"]
                        ["object"]),
                (build1.node
                        ["get_starting_jobs_03"]
                        ["object"])]

        (build1.node
                ["get_starting_jobs_01"]
                ["object"].should_run) = True
        (build1.node
                ["get_starting_jobs_01"]
                ["object"].parents_should_not_run) = True
        (build1.node
                ["get_starting_jobs_02"]
                ["object"].should_run) = True
        (build1.node
                ["get_starting_jobs_02"]
                ["object"].parents_should_not_run) = False
        (build1.node
                ["get_starting_jobs_03"]
                ["object"].should_run) = True
        (build1.node
                ["get_starting_jobs_03"]
                ["object"].parents_should_not_run) = True
        (build1.node
                ["get_starting_jobs_04"]
                ["object"].should_run) = False
        (build1.node
                ["get_starting_jobs_04"]
                ["object"].parents_should_not_run) = True

        # when
        starting_jobs = build1.get_starting_jobs()

        # then
        self.assertItemsEqual(starting_jobs, expected_starting_jobs)

    @testing.unit
    def test_update_lower_nodes_should_run(self):
        # Given
        jobs = [
            UpdateLowerNodesShouldRunTop(),
            UpdateLowerNodesShouldRunBottom(),
            UpdateLowerNodesShouldRunLowest(),
            UpdateLowerNodesShouldRunMiddle01(),
            UpdateLowerNodesShouldRunMiddle02(),
        ]

        build = builder.build.Build(jobs)

        build_context = {
                "start_job": "update_lower_nodes_should_run_lowest", # UpdateLowerNodesShouldRunLowest,
        }

        build.construct_build_graph(build_context)

        top_job = (build.node
            ["update_lower_nodes_should_run_top"]
            ["object"])
        middle_job_01 = (build.node
            ["update_lower_nodes_should_run_middle_01"]
            ["object"])
        middle_job_02 = (build.node
            ["update_lower_nodes_should_run_middle_02"]
            ["object"])
        bottom_job = (build.node
            ["update_lower_nodes_should_run_bottom"]
            ["object"])
        lowest_job = (build.node
            ["update_lower_nodes_should_run_lowest"]
            ["object"])

        # Given
        expected_state1 = [True, False, False, False, True]
        expected_state2 = [False, True, True, False, True]
        expected_state3 = [False, False, False, True, True]
        expected_state4 = [False, False, False, False, True]

        # Starting state
        top_job.buildable = True
        top_job.stale = True
        middle_job_01.buildable = True
        middle_job_01.stale = True
        middle_job_02.buildable = True
        middle_job_02.stale = True
        bottom_job.buildable = True
        bottom_job.stale = True
        lowest_job.buildable = True
        lowest_job.stale = True

        # When
        state1 = [
                top_job.get_should_run(build),
                middle_job_01.get_should_run(build),
                middle_job_02.get_should_run(build),
                bottom_job.get_should_run(build),
                lowest_job.get_should_run(build),
        ]

        top_job.stale = False
        top_job.update_lower_nodes_should_run(build)
        state2 = [
                top_job.get_should_run(build),
                middle_job_01.get_should_run(build),
                middle_job_02.get_should_run(build),
                bottom_job.get_should_run(build),
                lowest_job.get_should_run(build),
        ]

        cache_set = set([])
        update_set = set([])
        middle_job_01.stale = False
        middle_job_02.stale = False
        middle_job_01.update_lower_nodes_should_run(build, cache_set=cache_set, update_set=update_set)
        middle_job_02.update_lower_nodes_should_run(build, cache_set=cache_set, update_set=update_set)
        state3 = [
                top_job.get_should_run(build),
                middle_job_01.get_should_run(build),
                middle_job_02.get_should_run(build),
                bottom_job.get_should_run(build),
                lowest_job.get_should_run(build),
        ]

        bottom_job.stale = False
        bottom_job.update_lower_nodes_should_run(build)
        state4 = [
                top_job.get_should_run(build),
                middle_job_01.get_should_run(build),
                middle_job_02.get_should_run(build),
                bottom_job.get_should_run(build),
                lowest_job.get_should_run(build),
        ]

        # Then
        self.assertListEqual(state1, expected_state1)
        self.assertListEqual(state2, expected_state2)
        self.assertListEqual(state3, expected_state3)
        self.assertListEqual(state4, expected_state4)
        self.assertEqual(top_job.count, 5)
        self.assertEqual(middle_job_01.count, 6)
        self.assertEqual(middle_job_02.count, 6)
        self.assertEqual(bottom_job.count, 7)
        self.assertEqual(lowest_job.count, 7)

    @testing.unit
    def test_get_next_jobs_to_run(self):
        # Given
        jobs = [
            GetNextJobsToRunTop(),
            GetNextJobsToRunBottom(),
            GetNextJobsToRunLowest(),
            GetNextJobsToRunMiddle01(),
            GetNextJobsToRunMiddle02(),
        ]

        build = builder.build.Build(jobs)

        build_context = {
                "start_job": "get_next_jobs_to_run_lowest", # GetNextJobsToRunLowest,
        }

        build.construct_build_graph(build_context)

        top_job = (build.node
                ["get_next_jobs_to_run_top"]
                ["object"])
        middle_01_job = (build.node
                ["get_next_jobs_to_run_middle_01"]
                ["object"])
        middle_02_job = (build.node
                ["get_next_jobs_to_run_middle_02"]
                ["object"])
        bottom_job = (build.node
                ["get_next_jobs_to_run_bottom"]
                ["object"])
        lowest_job = (build.node
                ["get_next_jobs_to_run_lowest"]
                ["object"])

        # state 1
        expected_next_run_list1 = [
                "get_next_jobs_to_run_top",
        ]

        expected_next_run_list2 = [
                "get_next_jobs_to_run_middle_01",
                "get_next_jobs_to_run_middle_02",
        ]

        expected_next_run_list3 = [
                "get_next_jobs_to_run_bottom",
        ]

        expected_next_run_list4 = [
                "get_next_jobs_to_run_lowest",
        ]

        # When
        top_job.should_run = True
        middle_01_job.should_run = False
        middle_02_job.should_run = False
        bottom_job.should_run = False
        lowest_job.should_run = False
        next_run_list1 = build.get_next_jobs_to_run(
                "get_next_jobs_to_run_top")

        top_job.should_run = False
        middle_01_job.should_run = True
        middle_02_job.should_run = True
        bottom_job.should_run = False
        lowest_job.should_run = False
        next_run_list2 = build.get_next_jobs_to_run(
                "get_next_jobs_to_run_top")

        top_job.should_run = False
        middle_01_job.should_run = False
        middle_02_job.should_run = False
        bottom_job.should_run = True
        lowest_job.should_run = False
        next_run_list3 = build.get_next_jobs_to_run(
                "get_next_jobs_to_run_top")

        top_job.should_run = False
        middle_01_job.should_run = False
        middle_02_job.should_run = False
        bottom_job.should_run = False
        lowest_job.should_run = True
        next_run_list4 = build.get_next_jobs_to_run(
                "get_next_jobs_to_run_top")

        # Then
        lists = [
                [expected_next_run_list1, next_run_list1],
                [expected_next_run_list2, next_run_list2],
                [expected_next_run_list3, next_run_list3],
                [expected_next_run_list4, next_run_list4],
        ]
        for list_set in lists:
            expected_list = list_set[0]
            actual_list = list_set[1]
            for actual_node in actual_list:
                self.assertIn(actual_node, expected_list)

    @testing.unit
    def test_update_job_cache(self):
        # Given
        jobs = [
            UpdateJobCacheTop(),
            UpdateJobCacheMiddle01(),
            UpdateJobCacheMiddle02(),
            UpdateJobCacheMiddle03(),
            UpdateJobCacheBottom(),
        ]

        build = builder.build.Build(jobs)

        build_context = {
                "start_job": "update_job_cache_bottom", # UpdateJobCacheBottom,
        }

        build.construct_build_graph(build_context)

        mtime_dict = {
                "update_job_cache_top_01_target": None,
                "update_job_cache_top_02_target": 100,
                "update_job_cache_top_03_target": 100,
        }

        (build.node
                ["update_job_cache_highest_target"]
                ["object"].mtime) = 100
        (build.node
                ["update_job_cache_highest_target"]
                ["object"].exists) = False
        (build.node
                ["update_job_cache_top_01_target"]
                ["object"].mtime) = None
        (build.node
                ["update_job_cache_top_01_target"]
                ["object"].exists) = False
        (build.node
                ["update_job_cache_top_02_target"]
                ["object"].mtime) = None
        (build.node
                ["update_job_cache_top_02_target"]
                ["object"].exists) = False
        (build.node
                ["update_job_cache_top_03_target"]
                ["object"].mtime) = 100
        (build.node
                ["update_job_cache_top_03_target"]
                ["object"].exists) = True
        (build.node
                ["update_job_cache_middle_02_target"]
                ["object"].mtime) = 50
        (build.node
                ["update_job_cache_middle_02_target"]
                ["object"].exists) = True
        (build.node
                ["update_job_cache_middle_03_target"]
                ["object"].mtime) = 150
        (build.node
                ["update_job_cache_middle_03_target"]
                ["object"].exists) = True

        mock_mtime = self.mock_mtime_generator(mtime_dict)

        expected_mtime_old1 = None
        expected_mtime_old2 = None
        expected_mtime_old3 = 100
        expected_mtime_new1 = None
        expected_mtime_new2 = 100
        expected_mtime_new3 = 100

        expected_stale_old1 = True
        expected_stale_old2 = False
        expected_stale_old3 = False
        expected_stale_new1 = True
        expected_stale_new2 = True
        expected_stale_new3 = False

        expected_buildable_old1 = False
        expected_buildable_old2 = False
        expected_buildable_old3 = True
        expected_buildable_new1 = False
        expected_buildable_new2 = True
        expected_buildable_new3 = True

        expected_should_run_old1 = False
        expected_should_run_old2 = False
        expected_should_run_old3 = False
        expected_should_run_new1 = False
        expected_should_run_new2 = True
        expected_should_run_new3 = False

        # When
        mtime_old1 = (build.node
                ["update_job_cache_top_01_target"]
                ["object"].get_mtime())
        mtime_old2 = (build.node
                ["update_job_cache_top_02_target"]
                ["object"].get_mtime())
        mtime_old3 = (build.node
                ["update_job_cache_top_03_target"]
                ["object"].get_mtime())
        stale_old1 = (build.node
                ["update_job_cache_middle_01"]
                ["object"].get_stale(build))
        stale_old2 = (build.node
                ["update_job_cache_middle_02"]
                ["object"].get_stale(build))
        stale_old3 = (build.node
                ["update_job_cache_middle_03"]
                ["object"].get_stale(build))
        buildable_old1 = (build.node
                ["update_job_cache_middle_01"]
                ["object"].get_buildable(build))
        buildable_old2 = (build.node
                ["update_job_cache_middle_02"]
                ["object"].get_buildable(build))
        buildable_old3 = (build.node
                ["update_job_cache_middle_03"]
                ["object"].get_buildable(build))
        should_run_old1 = (build.node
                ["update_job_cache_middle_01"]
                ["object"].get_should_run(build))
        should_run_old2 = (build.node
                ["update_job_cache_middle_02"]
                ["object"].get_should_run(build))
        should_run_old3 = (build.node
                ["update_job_cache_middle_03"]
                ["object"].get_should_run(build))

        with mock.patch("os.stat", mock_mtime):
            build.update_job_cache("update_job_cache_top")

        mtime_new1 = (build.node
                ["update_job_cache_top_01_target"]
                ["object"].get_mtime())
        mtime_new2 = (build.node
                ["update_job_cache_top_02_target"]
                ["object"].get_mtime())
        mtime_new3 = (build.node
                ["update_job_cache_top_03_target"]
                ["object"].get_mtime())
        stale_new1 = (build.node
                ["update_job_cache_middle_01"]
                ["object"].get_stale(build))
        stale_new2 = (build.node
                ["update_job_cache_middle_02"]
                ["object"].get_stale(build))
        stale_new3 = (build.node
                ["update_job_cache_middle_03"]
                ["object"].get_stale(build))
        buildable_new1 = (build.node
                ["update_job_cache_middle_01"]
                ["object"].get_buildable(build))
        buildable_new2 = (build.node
                ["update_job_cache_middle_02"]
                ["object"].get_buildable(build))
        buildable_new3 = (build.node
                ["update_job_cache_middle_03"]
                ["object"].get_buildable(build))
        should_run_new1 = (build.node
                ["update_job_cache_middle_01"]
                ["object"].get_should_run(build))
        should_run_new2 = (build.node
                ["update_job_cache_middle_02"]
                ["object"].get_should_run(build))
        should_run_new3 = (build.node
                ["update_job_cache_middle_03"]
                ["object"].get_should_run(build))

        # Then
        self.assertEqual(mtime_old1, expected_mtime_old1)
        self.assertEqual(mtime_old2, expected_mtime_old2)
        self.assertEqual(mtime_old3, expected_mtime_old3)
        self.assertEqual(stale_old1, expected_stale_old1)
        self.assertEqual(stale_old2, expected_stale_old2)
        self.assertEqual(stale_old3, expected_stale_old3)
        self.assertEqual(buildable_old1, expected_buildable_old1)
        self.assertEqual(buildable_old2, expected_buildable_old2)
        self.assertEqual(buildable_old3, expected_buildable_old3)
        self.assertEqual(should_run_old1, expected_should_run_old1)
        self.assertEqual(should_run_old2, expected_should_run_old2)
        self.assertEqual(should_run_old3, expected_should_run_old3)
        self.assertEqual(mtime_new1, expected_mtime_new1)
        self.assertEqual(mtime_new2, expected_mtime_new2)
        self.assertEqual(mtime_new3, expected_mtime_new3)
        self.assertEqual(stale_new1, expected_stale_new1)
        self.assertEqual(stale_new2, expected_stale_new2)
        self.assertEqual(stale_new3, expected_stale_new3)
        self.assertEqual(buildable_new1, expected_buildable_new1)
        self.assertEqual(buildable_new2, expected_buildable_new2)
        self.assertEqual(buildable_new3, expected_buildable_new3)
        self.assertEqual(should_run_new1, expected_should_run_new1)
        self.assertEqual(should_run_new2, expected_should_run_new2)
        self.assertEqual(should_run_new3, expected_should_run_new3)

    @testing.unit
    def test_expand_exact(self):
        # Given
        jobs = [
            ExpandExactTop(),
            ExpandExactMiddle(),
            ExpandExactBottom(),
        ]

        build_context = {
                "start_job": "test_expand_exact_middle", # ExpandExactMiddle,
                "exact": True,
        }

        build = builder.build.Build(jobs)

        # When
        build.construct_build_graph(build_context)

        # Then
        self.assertEqual(len(build.node), 4)


    @testing.unit
    def test_force_build(self):
        # Given
        jobs = [
            ForceBuildTop(),
            ForceBuildMiddle(),
            ForceBuildBottom(),
        ]

        build_context = {
                "start_time": arrow.get("2014-12-05-11-45"),
                "end_time": arrow.get("2014-12-05-12-00"),
                "force": True,
                "start_job": "force_build_bottom", # ForceBuildBottom,
                "depth": 2,
        }

        build = builder.build.Build(jobs)

        # When
        build.construct_build_graph(build_context)

        # Then
        count = 0
        for node_id, node in build.node.iteritems():
            if node.get("object") is None:
                continue
            if not isinstance(node["object"], builder.jobs.JobState):
                continue
            if "top" in node_id:
                count = count + 1
                self.assertTrue(node["object"].build_context.get("force", False))
            else:
                self.assertFalse(node["object"].build_context.get("force", False))
        self.assertEqual(count, 15)

    @testing.unit
    def test_update_target_cache(self):
        # Given
        jobs = [
            UpdateTargetCacheMiddle01(),
            UpdateTargetCacheMiddle02(),
            UpdateTargetCacheMiddle03(),
            UpdateTargetCacheBottom(),
            UpdateTargetCacheTop(),
        ]

        build = builder.build.Build(jobs)

        build_context = {
                "start_job": "update_target_cache_bottom", # UpdateTargetCacheBottom,
        }

        build.construct_build_graph(build_context)

        mtime_dict = {
                "update_target_cache_top_01_target": None,
                "update_target_cache_top_02_target": 100,
                "update_target_cache_top_03_target": 100,
        }

        (build.node
                ["update_target_cache_top_01_target"]
                ["object"].mtime) = None
        (build.node
                ["update_target_cache_top_01_target"]
                ["object"].exists) = False
        (build.node
                ["update_target_cache_top_02_target"]
                ["object"].mtime) = None
        (build.node
                ["update_target_cache_top_02_target"]
                ["object"].exists) = False
        (build.node
                ["update_target_cache_top_03_target"]
                ["object"].mtime) = 100
        (build.node
                ["update_target_cache_top_03_target"]
                ["object"].exists) = True
        (build.node
                ["update_target_cache_middle_02_target"]
                ["object"].mtime) = 50
        (build.node
                ["update_target_cache_middle_02_target"]
                ["object"].exists) = True
        (build.node
                ["update_target_cache_middle_03_target"]
                ["object"].mtime) = 150
        (build.node
                ["update_target_cache_middle_03_target"]
                ["object"].exists) = True

        mock_mtime = self.mock_mtime_generator(mtime_dict)

        expected_mtime_old1 = None
        expected_mtime_old2 = None
        expected_mtime_old3 = 100
        expected_mtime_new1 = None
        expected_mtime_new2 = 100
        expected_mtime_new3 = 100

        expected_stale_old1 = True
        expected_stale_old2 = False
        expected_stale_old3 = False
        expected_stale_new1 = True
        expected_stale_new2 = True
        expected_stale_new3 = False

        expected_buildable_old1 = False
        expected_buildable_old2 = False
        expected_buildable_old3 = True
        expected_buildable_new1 = False
        expected_buildable_new2 = True
        expected_buildable_new3 = True

        expected_should_run_old1 = False
        expected_should_run_old2 = False
        expected_should_run_old3 = False
        expected_should_run_new1 = False
        expected_should_run_new2 = True
        expected_should_run_new3 = False

        # When
        mtime_old1 = (build.node
                ["update_target_cache_top_01_target"]
                ["object"].get_mtime())
        mtime_old2 = (build.node
                ["update_target_cache_top_02_target"]
                ["object"].get_mtime())
        mtime_old3 = (build.node
                ["update_target_cache_top_03_target"]
                ["object"].get_mtime())
        stale_old1 = (build.node
                ["update_target_cache_middle_01"]
                ["object"].get_stale(build))
        stale_old2 = (build.node
                ["update_target_cache_middle_02"]
                ["object"].get_stale(build))
        stale_old3 = (build.node
                ["update_target_cache_middle_03"]
                ["object"].get_stale(build))
        buildable_old1 = (build.node
                ["update_target_cache_middle_01"]
                ["object"].get_buildable(build))
        buildable_old2 = (build.node
                ["update_target_cache_middle_02"]
                ["object"].get_buildable(build))
        buildable_old3 = (build.node
                ["update_target_cache_middle_03"]
                ["object"].get_buildable(build))
        should_run_old1 = (build.node
                ["update_target_cache_middle_01"]
                ["object"].get_should_run(build))
        should_run_old2 = (build.node
                ["update_target_cache_middle_02"]
                ["object"].get_should_run(build))
        should_run_old3 = (build.node
                ["update_target_cache_middle_03"]
                ["object"].get_should_run(build))

        with mock.patch("os.stat", mock_mtime):
            build.update_target_cache("update_target_cache_top_01_target")
            build.update_target_cache("update_target_cache_top_02_target")
            build.update_target_cache("update_target_cache_top_03_target")

        mtime_new1 = (build.node
                ["update_target_cache_top_01_target"]
                ["object"].get_mtime())
        mtime_new2 = (build.node
                ["update_target_cache_top_02_target"]
                ["object"].get_mtime())
        mtime_new3 = (build.node
                ["update_target_cache_top_03_target"]
                ["object"].get_mtime())
        stale_new1 = (build.node
                ["update_target_cache_middle_01"]
                ["object"].get_stale(build))
        stale_new2 = (build.node
                ["update_target_cache_middle_02"]
                ["object"].get_stale(build))
        stale_new3 = (build.node
                ["update_target_cache_middle_03"]
                ["object"].get_stale(build))
        buildable_new1 = (build.node
                ["update_target_cache_middle_01"]
                ["object"].get_buildable(build))
        buildable_new2 = (build.node
                ["update_target_cache_middle_02"]
                ["object"].get_buildable(build))
        buildable_new3 = (build.node
                ["update_target_cache_middle_03"]
                ["object"].get_buildable(build))
        should_run_new1 = (build.node
                ["update_target_cache_middle_01"]
                ["object"].get_should_run(build))
        should_run_new2 = (build.node
                ["update_target_cache_middle_02"]
                ["object"].get_should_run(build))
        should_run_new3 = (build.node
                ["update_target_cache_middle_03"]
                ["object"].get_should_run(build))

        # Then
        self.assertEqual(mtime_old1, expected_mtime_old1)
        self.assertEqual(mtime_old2, expected_mtime_old2)
        self.assertEqual(mtime_old3, expected_mtime_old3)
        self.assertEqual(stale_old1, expected_stale_old1)
        self.assertEqual(stale_old2, expected_stale_old2)
        self.assertEqual(stale_old3, expected_stale_old3)
        self.assertEqual(buildable_old1, expected_buildable_old1)
        self.assertEqual(buildable_old2, expected_buildable_old2)
        self.assertEqual(buildable_old3, expected_buildable_old3)
        self.assertEqual(should_run_old1, expected_should_run_old1)
        self.assertEqual(should_run_old2, expected_should_run_old2)
        self.assertEqual(should_run_old3, expected_should_run_old3)
        self.assertEqual(mtime_new1, expected_mtime_new1)
        self.assertEqual(mtime_new2, expected_mtime_new2)
        self.assertEqual(mtime_new3, expected_mtime_new3)
        self.assertEqual(stale_new1, expected_stale_new1)
        self.assertEqual(stale_new2, expected_stale_new2)
        self.assertEqual(stale_new3, expected_stale_new3)
        self.assertEqual(buildable_new1, expected_buildable_new1)
        self.assertEqual(buildable_new2, expected_buildable_new2)
        self.assertEqual(buildable_new3, expected_buildable_new3)
        self.assertEqual(should_run_new1, expected_should_run_new1)
        self.assertEqual(should_run_new2, expected_should_run_new2)
        self.assertEqual(should_run_new3, expected_should_run_new3)

    @testing.unit
    def test_finish(self):
        # Given
        jobs = [
            UpdateJobCacheTop(),
            UpdateJobCacheMiddle01(),
            UpdateJobCacheMiddle02(),
            UpdateJobCacheMiddle03(),
            UpdateJobCacheBottom(),
        ]

        build = builder.build.Build(jobs)

        build_context = {
                "start_job": "update_job_cache_bottom", # UpdateJobCacheBottom,
        }

        build.construct_build_graph(build_context)

        mtime_dict = {
                "update_job_cache_top_01_target": None,
                "update_job_cache_top_02_target": 100,
                "update_job_cache_top_03_target": 100,
        }

        (build.node
                ["update_job_cache_highest_target"]
                ["object"].mtime) = 100
        (build.node
                ["update_job_cache_highest_target"]
                ["object"].exists) = False
        (build.node
                ["update_job_cache_top_01_target"]
                ["object"].mtime) = None
        (build.node
                ["update_job_cache_top_01_target"]
                ["object"].exists) = False
        (build.node
                ["update_job_cache_top_02_target"]
                ["object"].mtime) = None
        (build.node
                ["update_job_cache_top_02_target"]
                ["object"].exists) = False
        (build.node
                ["update_job_cache_top_03_target"]
                ["object"].mtime) = 100
        (build.node
                ["update_job_cache_top_03_target"]
                ["object"].exists) = True
        (build.node
                ["update_job_cache_middle_02_target"]
                ["object"].mtime) = 50
        (build.node
                ["update_job_cache_middle_02_target"]
                ["object"].exists) = True
        (build.node
                ["update_job_cache_middle_03_target"]
                ["object"].mtime) = 150
        (build.node
                ["update_job_cache_middle_03_target"]
                ["object"].exists) = True

        mock_mtime = self.mock_mtime_generator(mtime_dict)

        expected_mtime_old1 = None
        expected_mtime_old2 = None
        expected_mtime_old3 = 100
        expected_mtime_new1 = None
        expected_mtime_new2 = 100
        expected_mtime_new3 = 100

        expected_stale_old1 = True
        expected_stale_old2 = False
        expected_stale_old3 = False
        expected_stale_new1 = True
        expected_stale_new2 = True
        expected_stale_new3 = False

        expected_buildable_old1 = False
        expected_buildable_old2 = False
        expected_buildable_old3 = True
        expected_buildable_new1 = False
        expected_buildable_new2 = True
        expected_buildable_new3 = True

        expected_should_run_old1 = False
        expected_should_run_old2 = False
        expected_should_run_old3 = False
        expected_should_run_new1 = False
        expected_should_run_new2 = True
        expected_should_run_new3 = False

        build.run = mock.Mock()

        # When
        mtime_old1 = (build.node
                ["update_job_cache_top_01_target"]
                ["object"].get_mtime())
        mtime_old2 = (build.node
                ["update_job_cache_top_02_target"]
                ["object"].get_mtime())
        mtime_old3 = (build.node
                ["update_job_cache_top_03_target"]
                ["object"].get_mtime())
        stale_old1 = (build.node
                ["update_job_cache_middle_01"]
                ["object"].get_stale(build))
        stale_old2 = (build.node
                ["update_job_cache_middle_02"]
                ["object"].get_stale(build))
        stale_old3 = (build.node
                ["update_job_cache_middle_03"]
                ["object"].get_stale(build))
        buildable_old1 = (build.node
                ["update_job_cache_middle_01"]
                ["object"].get_buildable(build))
        buildable_old2 = (build.node
                ["update_job_cache_middle_02"]
                ["object"].get_buildable(build))
        buildable_old3 = (build.node
                ["update_job_cache_middle_03"]
                ["object"].get_buildable(build))
        should_run_old1 = (build.node
                ["update_job_cache_middle_01"]
                ["object"].get_should_run(build))
        should_run_old2 = (build.node
                ["update_job_cache_middle_02"]
                ["object"].get_should_run(build))
        should_run_old3 = (build.node
                ["update_job_cache_middle_03"]
                ["object"].get_should_run(build))


        with mock.patch("os.stat", mock_mtime):
            build.finish("update_job_cache_top")

        mtime_new1 = (build.node
                ["update_job_cache_top_01_target"]
                ["object"].get_mtime())
        mtime_new2 = (build.node
                ["update_job_cache_top_02_target"]
                ["object"].get_mtime())
        mtime_new3 = (build.node
                ["update_job_cache_top_03_target"]
                ["object"].get_mtime())
        stale_new1 = (build.node
                ["update_job_cache_middle_01"]
                ["object"].get_stale(build))
        stale_new2 = (build.node
                ["update_job_cache_middle_02"]
                ["object"].get_stale(build))
        stale_new3 = (build.node
                ["update_job_cache_middle_03"]
                ["object"].get_stale(build))
        buildable_new1 = (build.node
                ["update_job_cache_middle_01"]
                ["object"].get_buildable(build))
        buildable_new2 = (build.node
                ["update_job_cache_middle_02"]
                ["object"].get_buildable(build))
        buildable_new3 = (build.node
                ["update_job_cache_middle_03"]
                ["object"].get_buildable(build))
        should_run_new1 = (build.node
                ["update_job_cache_middle_01"]
                ["object"].get_should_run(build))
        should_run_new2 = (build.node
                ["update_job_cache_middle_02"]
                ["object"].get_should_run(build))
        should_run_new3 = (build.node
                ["update_job_cache_middle_03"]
                ["object"].get_should_run(build))

        # Then
        self.assertEqual(mtime_old1, expected_mtime_old1)
        self.assertEqual(mtime_old2, expected_mtime_old2)
        self.assertEqual(mtime_old3, expected_mtime_old3)
        self.assertEqual(stale_old1, expected_stale_old1)
        self.assertEqual(stale_old2, expected_stale_old2)
        self.assertEqual(stale_old3, expected_stale_old3)
        self.assertEqual(buildable_old1, expected_buildable_old1)
        self.assertEqual(buildable_old2, expected_buildable_old2)
        self.assertEqual(buildable_old3, expected_buildable_old3)
        self.assertEqual(should_run_old1, expected_should_run_old1)
        self.assertEqual(should_run_old2, expected_should_run_old2)
        self.assertEqual(should_run_old3, expected_should_run_old3)
        self.assertEqual(mtime_new1, expected_mtime_new1)
        self.assertEqual(mtime_new2, expected_mtime_new2)
        self.assertEqual(mtime_new3, expected_mtime_new3)
        self.assertEqual(stale_new1, expected_stale_new1)
        self.assertEqual(stale_new2, expected_stale_new2)
        self.assertEqual(stale_new3, expected_stale_new3)
        self.assertEqual(buildable_new1, expected_buildable_new1)
        self.assertEqual(buildable_new2, expected_buildable_new2)
        self.assertEqual(buildable_new3, expected_buildable_new3)
        self.assertEqual(should_run_new1, expected_should_run_new1)
        self.assertEqual(should_run_new2, expected_should_run_new2)
        self.assertEqual(should_run_new3, expected_should_run_new3)
        build.run.assert_has_calls([mock.call("update_job_cache_middle_02")])

    @testing.unit
    def test_update(self):
        # Given
        jobs = [
            UpdateTargetCacheMiddle01(),
            UpdateTargetCacheMiddle02(),
            UpdateTargetCacheMiddle03(),
            UpdateTargetCacheBottom(),
            UpdateTargetCacheBottom(),
            UpdateTargetCacheTop(),
        ]

        build = builder.build.Build(jobs)

        build_context = {
                "start_job": "update_target_cache_bottom", # UpdateTargetCacheBottom,
        }

        build.construct_build_graph(build_context)

        mtime_dict = {
                "update_target_cache_top_01_target": None,
                "update_target_cache_top_02_target": 100,
                "update_target_cache_top_03_target": 100,
        }

        (build.node
                ["update_target_cache_top_01_target"]
                ["object"].mtime) = None
        (build.node
                ["update_target_cache_top_01_target"]
                ["object"].exists) = False
        (build.node
                ["update_target_cache_top_02_target"]
                ["object"].mtime) = None
        (build.node
                ["update_target_cache_top_02_target"]
                ["object"].exists) = False
        (build.node
                ["update_target_cache_top_03_target"]
                ["object"].mtime) = 100
        (build.node
                ["update_target_cache_top_03_target"]
                ["object"].exists) = True
        (build.node
                ["update_target_cache_middle_02_target"]
                ["object"].mtime) = 50
        (build.node
                ["update_target_cache_middle_02_target"]
                ["object"].exists) = True
        (build.node
                ["update_target_cache_middle_03_target"]
                ["object"].mtime) = 150
        (build.node
                ["update_target_cache_middle_03_target"]
                ["object"].exists) = True

        mock_mtime = self.mock_mtime_generator(mtime_dict)

        expected_mtime_old1 = None
        expected_mtime_old2 = None
        expected_mtime_old3 = 100
        expected_mtime_new1 = None
        expected_mtime_new2 = 100
        expected_mtime_new3 = 100

        expected_stale_old1 = True
        expected_stale_old2 = False
        expected_stale_old3 = False
        expected_stale_new1 = True
        expected_stale_new2 = True
        expected_stale_new3 = False

        expected_buildable_old1 = False
        expected_buildable_old2 = False
        expected_buildable_old3 = True
        expected_buildable_new1 = False
        expected_buildable_new2 = True
        expected_buildable_new3 = True

        expected_should_run_old1 = False
        expected_should_run_old2 = False
        expected_should_run_old3 = False
        expected_should_run_new1 = False
        expected_should_run_new2 = True
        expected_should_run_new3 = False

        build.run = mock.Mock()

        # When
        mtime_old1 = (build.node
                ["update_target_cache_top_01_target"]
                ["object"].get_mtime())
        mtime_old2 = (build.node
                ["update_target_cache_top_02_target"]
                ["object"].get_mtime())
        mtime_old3 = (build.node
                ["update_target_cache_top_03_target"]
                ["object"].get_mtime())
        stale_old1 = (build.node
                ["update_target_cache_middle_01"]
                ["object"].get_stale(build))
        stale_old2 = (build.node
                ["update_target_cache_middle_02"]
                ["object"].get_stale(build))
        stale_old3 = (build.node
                ["update_target_cache_middle_03"]
                ["object"].get_stale(build))
        buildable_old1 = (build.node
                ["update_target_cache_middle_01"]
                ["object"].get_buildable(build))
        buildable_old2 = (build.node
                ["update_target_cache_middle_02"]
                ["object"].get_buildable(build))
        buildable_old3 = (build.node
                ["update_target_cache_middle_03"]
                ["object"].get_buildable(build))
        should_run_old1 = (build.node
                ["update_target_cache_middle_01"]
                ["object"].get_should_run(build))
        should_run_old2 = (build.node
                ["update_target_cache_middle_02"]
                ["object"].get_should_run(build))
        should_run_old3 = (build.node
                ["update_target_cache_middle_03"]
                ["object"].get_should_run(build))

        with mock.patch("os.stat", mock_mtime):
            build.update("update_target_cache_top_01_target")
            build.update("update_target_cache_top_02_target")
            build.update("update_target_cache_top_03_target")

        mtime_new1 = (build.node
                ["update_target_cache_top_01_target"]
                ["object"].get_mtime())
        mtime_new2 = (build.node
                ["update_target_cache_top_02_target"]
                ["object"].get_mtime())
        mtime_new3 = (build.node
                ["update_target_cache_top_03_target"]
                ["object"].get_mtime())
        stale_new1 = (build.node
                ["update_target_cache_middle_01"]
                ["object"].get_stale(build))
        stale_new2 = (build.node
                ["update_target_cache_middle_02"]
                ["object"].get_stale(build))
        stale_new3 = (build.node
                ["update_target_cache_middle_03"]
                ["object"].get_stale(build))
        buildable_new1 = (build.node
                ["update_target_cache_middle_01"]
                ["object"].get_buildable(build))
        buildable_new2 = (build.node
                ["update_target_cache_middle_02"]
                ["object"].get_buildable(build))
        buildable_new3 = (build.node
                ["update_target_cache_middle_03"]
                ["object"].get_buildable(build))
        should_run_new1 = (build.node
                ["update_target_cache_middle_01"]
                ["object"].get_should_run(build))
        should_run_new2 = (build.node
                ["update_target_cache_middle_02"]
                ["object"].get_should_run(build))
        should_run_new3 = (build.node
                ["update_target_cache_middle_03"]
                ["object"].get_should_run(build))

        # Then
        self.assertEqual(mtime_old1, expected_mtime_old1)
        self.assertEqual(mtime_old2, expected_mtime_old2)
        self.assertEqual(mtime_old3, expected_mtime_old3)
        self.assertEqual(stale_old1, expected_stale_old1)
        self.assertEqual(stale_old2, expected_stale_old2)
        self.assertEqual(stale_old3, expected_stale_old3)
        self.assertEqual(buildable_old1, expected_buildable_old1)
        self.assertEqual(buildable_old2, expected_buildable_old2)
        self.assertEqual(buildable_old3, expected_buildable_old3)
        self.assertEqual(should_run_old1, expected_should_run_old1)
        self.assertEqual(should_run_old2, expected_should_run_old2)
        self.assertEqual(should_run_old3, expected_should_run_old3)
        self.assertEqual(mtime_new1, expected_mtime_new1)
        self.assertEqual(mtime_new2, expected_mtime_new2)
        self.assertEqual(mtime_new3, expected_mtime_new3)
        self.assertEqual(stale_new1, expected_stale_new1)
        self.assertEqual(stale_new2, expected_stale_new2)
        self.assertEqual(stale_new3, expected_stale_new3)
        self.assertEqual(buildable_new1, expected_buildable_new1)
        self.assertEqual(buildable_new2, expected_buildable_new2)
        self.assertEqual(buildable_new3, expected_buildable_new3)
        self.assertEqual(should_run_new1, expected_should_run_new1)
        self.assertEqual(should_run_new2, expected_should_run_new2)
        self.assertEqual(should_run_new3, expected_should_run_new3)
        build.run.assert_has_calls([mock.call("update_target_cache_middle_02")])

    @unittest.skip("There was a file that was not added properly. When it's time"
                  "to add large job expanders this will be fixed")
    @testing.unit
    def test_large_job_expander(self):
        jobs = [
            builder.tests_large_jobs.Job1Top,
            builder.tests_large_jobs.Job2Top,
            builder.tests_large_jobs.Job3Top,
            builder.tests_large_jobs.LargeJobExpanderTest,
        ]

        build = builder.build.Build(jobs)

        build_context = {
            "start_job": "large_job_expander", # deepy.build.tests_large_jobs.LargeJobExpanderTest
        }

        build.construct_build_graph(build_context)
