import pytest

from pipeline.full_evaluation import exclude_or_include_configs, filter_paths


class TestConfigFiltering:
    def test_filter_include_single_dir(self):
        assert filter_paths(['dir1/file1.yaml', 'dir1/file2.yaml', 'dir2/file1.yaml', 'dir2/file2.yaml'],
                            'dir1', must_include=True) == ['dir1/file1.yaml', 'dir1/file2.yaml']

    def test_filter_include_multiple_dir(self):
        assert filter_paths(['dir1/file1.yaml', 'dir1/file2.yaml', 'dir2/file1.yaml', 'dir2/file2.yaml',
                             'dir3/file1.yaml'],
                            'dir1,dir2', must_include=True) \
               == ['dir1/file1.yaml', 'dir1/file2.yaml', 'dir2/file1.yaml', 'dir2/file2.yaml']

    def test_filter_include_file_name(self):
        assert filter_paths(['dir1/file1.yaml', 'dir1/file2.yaml', 'dir2/file1.yaml', 'dir2/file2.yaml'],
                            'file1', must_include=True) == ['dir1/file1.yaml', 'dir2/file1.yaml']

    def test_filter_exclude_single_dir(self):
        assert filter_paths(['dir1/file1.yaml', 'dir1/file2.yaml', 'dir2/file1.yaml', 'dir2/file2.yaml'],
                            'dir1', must_include=False) == ['dir2/file1.yaml', 'dir2/file2.yaml']

    def test_filter_exclude_multiple_dir(self):
        assert filter_paths(['dir1/file1.yaml', 'dir1/file2.yaml', 'dir2/file1.yaml', 'dir2/file2.yaml',
                             'dir3/file1.yaml'],
                            'dir1,dir2', must_include=False) == ['dir3/file1.yaml']

    def test_filter_exclude_file_name(self):
        assert filter_paths(['dir1/file1.yaml', 'dir1/file2.yaml', 'dir2/file1.yaml', 'dir2/file2.yaml'],
                            'file1', must_include=False) == ['dir1/file2.yaml', 'dir2/file2.yaml']

    def test_both_include_and_exclude(self):
        with pytest.raises(ValueError):
            exclude_or_include_configs("dir1", "dir2",
                                       ['dir1/file1.yaml', 'dir1/file2.yaml', 'dir2/file1.yaml', 'dir2/file2.yaml'])
