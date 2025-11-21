"""Unit tests for dataset loaders and diff masking"""
import pytest
from sven_data.loaders import BigVulDataset, CrossVulDataset, VUDENCDataset
from sven_data.interfaces import DatasetRegistry
from sven_data.schemas import DatasetConfig


def test_diff_masking_simple():
    """Test basic diff masking logic"""
    loader = BigVulDataset()
    
    vulnerable = "x = input()"
    fixed = "x = sanitize(input())"
    
    mask = loader.apply_diff_masking(vulnerable, fixed)
    
    # Mask should indicate changes
    assert isinstance(mask, list)
    assert len(mask) > 0
    assert all(m in [0, 1] for m in mask)


def test_diff_masking_no_change():
    """Test diff masking when code is identical"""
    loader = BigVulDataset()
    
    code = "def foo(): pass"
    mask = loader.apply_diff_masking(code, code)
    
    # All tokens should be unchanged
    assert all(m == 0 for m in mask)


def test_diff_masking_complete_change():
    """Test diff masking when all code changes"""
    loader = BigVulDataset()
    
    vulnerable = "a b c"
    fixed = "x y z"
    
    mask = loader.apply_diff_masking(vulnerable, fixed)
    
    # All tokens should be marked as changed
    assert all(m == 1 for m in mask)


def test_dataset_registry():
    """Test that datasets are registered correctly"""
    # Should be able to get loaders by name
    big_vul = DatasetRegistry.get_loader("big_vul")
    assert isinstance(big_vul, BigVulDataset)
    
    cross_vul = DatasetRegistry.get_loader("cross_vul")
    assert isinstance(cross_vul, CrossVulDataset)
    
    vudenc = DatasetRegistry.get_loader("vudenc")
    assert isinstance(vudenc, VUDENCDataset)


def test_dataset_registry_unknown():
    """Test that unknown dataset raises error"""
    with pytest.raises(ValueError, match="Unknown dataset"):
        DatasetRegistry.get_loader("nonexistent")


def test_dataset_load_config():
    """Test that loaders accept config"""
    config = DatasetConfig(
        name="big_vul",
        language="python",
        split="train",
        max_samples=100
    )
    
    loader = BigVulDataset()
    # Should not raise (returns empty list for now)
    result = loader.load(config)
    assert isinstance(result, list)


def test_dataset_iterator():
    """Test batched iterator"""
    config = DatasetConfig(
        name="big_vul",
        language="python",
        split="train"
    )
    
    loader = BigVulDataset()
    iterator = loader.get_iterator(config, batch_size=4)
    
    # Should be an iterator
    assert hasattr(iterator, '__iter__')
    assert hasattr(iterator, '__next__')


def test_diff_masking_sql_injection():
    """Test diff masking on realistic SQL injection fix"""
    loader = BigVulDataset()
    
    vulnerable = 'query = "SELECT * FROM users WHERE id=" + user_id'
    fixed = 'query = "SELECT * FROM users WHERE id=?" ; cursor.execute(query, (user_id,))'
    
    mask = loader.apply_diff_masking(vulnerable, fixed)
    
    # Should detect the change from concatenation to parameterized
    assert sum(mask) > 0  # At least some tokens changed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
