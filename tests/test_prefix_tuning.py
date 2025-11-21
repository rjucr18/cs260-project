"""Unit tests for prefix tuning modules"""
import pytest
import torch
from prefix_tuning.secure_prefix import (
    BasePrefixTuning,
    SecurePrefixTuning,
    VulnerablePrefixTuning,
    PrefixConfig,
)


def test_prefix_config_defaults():
    """Test default configuration"""
    config = PrefixConfig()
    assert config.prefix_length == 20
    assert config.hidden_dim == 512
    assert config.init == "random"


def test_base_prefix_initialization():
    """Test prefix module initialization with correct dimensions"""
    config = PrefixConfig(prefix_length=16, hidden_dim=1024)
    prefix = BasePrefixTuning(config)
    
    assert prefix.prefix.shape == (16, 1024)
    assert prefix.prefix.requires_grad


def test_prefix_with_projection():
    """Test prefix with projection to target dimension"""
    config = PrefixConfig(prefix_length=20, hidden_dim=512)
    prefix = BasePrefixTuning(config, target_hidden_dim=1024)
    
    # Should have projection layer
    assert prefix.proj is not None
    assert prefix.target_hidden_dim == 1024
    
    # Output should be projected dimension
    output = prefix.get_prefix_embeddings()
    assert output.shape == (20, 1024)


def test_prefix_without_projection():
    """Test prefix without projection (matching dims)"""
    config = PrefixConfig(prefix_length=20, hidden_dim=1024)
    prefix = BasePrefixTuning(config, target_hidden_dim=1024)
    
    # Should NOT have projection layer
    assert prefix.proj is None
    
    output = prefix.get_prefix_embeddings()
    assert output.shape == (20, 1024)


def test_secure_vs_vulnerable_independence():
    """Test that secure and vulnerable prefixes are independent"""
    config = PrefixConfig(prefix_length=10, hidden_dim=512)
    
    secure = SecurePrefixTuning(config)
    vulnerable = VulnerablePrefixTuning(config)
    
    # Should be different objects with different parameters
    assert secure is not vulnerable
    assert not torch.allclose(secure.prefix, vulnerable.prefix)


def test_prefix_forward():
    """Test forward pass returns correct shape"""
    config = PrefixConfig(prefix_length=8, hidden_dim=256)
    prefix = SecurePrefixTuning(config, target_hidden_dim=512)
    
    output = prefix.forward()
    assert output.shape == (8, 512)
    assert output.requires_grad


def test_prefix_save_load(tmp_path):
    """Test save and load functionality"""
    config = PrefixConfig(prefix_length=12, hidden_dim=768)
    original = SecurePrefixTuning(config)
    
    # Save
    save_path = tmp_path / "prefix.pt"
    original.save(str(save_path))
    
    # Load
    loaded = SecurePrefixTuning.load(str(save_path))
    
    # Should have same parameters
    assert loaded.config.prefix_length == config.prefix_length
    assert loaded.config.hidden_dim == config.hidden_dim
    assert torch.allclose(loaded.prefix, original.prefix)


def test_prefix_gradient_flow():
    """Test that gradients flow through prefix parameters"""
    config = PrefixConfig(prefix_length=5, hidden_dim=128)
    prefix = BasePrefixTuning(config)
    
    # Forward and backward
    output = prefix.forward()
    loss = output.sum()
    loss.backward()
    
    # Gradient should exist
    assert prefix.prefix.grad is not None
    assert prefix.prefix.grad.shape == prefix.prefix.shape


def test_batch_prefix_expansion():
    """Test that prefix can be expanded for batching"""
    config = PrefixConfig(prefix_length=10, hidden_dim=256)
    prefix = SecurePrefixTuning(config)
    
    embeddings = prefix.get_prefix_embeddings()
    
    # Expand to batch
    batch_size = 4
    batched = embeddings.unsqueeze(0).expand(batch_size, -1, -1)
    
    assert batched.shape == (batch_size, 10, 256)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
