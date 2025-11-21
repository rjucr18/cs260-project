"""
Validation script to test Priority 0, 1, 2 implementations.
Run this to verify everything is working.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

def test_priority_0():
    """Test Priority 0: Repo stabilization"""
    print("Testing Priority 0: Repo stabilization...")
    
    # Test imports
    try:
        import torch
        import transformers
        import flask
        import yaml
        print("  ✓ All dependencies installed")
    except ImportError as e:
        print(f"  ✗ Missing dependency: {e}")
        return False
    
    # Test config loading
    try:
        import yaml
        with open("configs/python.yaml") as f:
            config = yaml.safe_load(f)
        assert config["model"]["prefix_hidden_dim"] == 1024
        assert config["model"]["seed"] == 42
        assert config["training"]["amp_enabled"] == True
        print("  ✓ Config file valid")
    except Exception as e:
        print(f"  ✗ Config error: {e}")
        return False
    
    return True


def test_priority_1():
    """Test Priority 1: Data pipeline"""
    print("\nTesting Priority 1: Data pipeline...")
    
    try:
        from sven_data.loaders import BigVulDataset, DatasetRegistry
        from sven_data.schemas import DatasetConfig
        
        # Test dataset registry
        loader = DatasetRegistry.get_loader("big_vul")
        assert isinstance(loader, BigVulDataset)
        print("  ✓ Dataset registry working")
        
        # Test diff masking
        loader = BigVulDataset()
        vulnerable = "x = input()"
        fixed = "x = sanitize(input())"
        mask = loader.apply_diff_masking(vulnerable, fixed)
        assert len(mask) > 0
        assert all(m in [0, 1] for m in mask)
        print("  ✓ Diff masking working")
        
        # Test config loading
        config = DatasetConfig(
            name="big_vul",
            language="python",
            split="train"
        )
        data = loader.load(config)
        assert isinstance(data, list)
        print("  ✓ Dataset loader interface working")
        
    except Exception as e:
        print(f"  ✗ Data pipeline error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_priority_2():
    """Test Priority 2: Three-loss training"""
    print("\nTesting Priority 2: Three-loss training...")
    
    try:
        import torch
        from models.codegen_wrapper import CodeGenWrapper
        from training.train import Trainer, TrainerConfig
        
        # Test model with loss computation
        print("  Creating model (lazy_load=True, no download)...")
        model = CodeGenWrapper(
            secure=True,
            lazy_load=True,
            use_sdpa=True
        )
        
        # Test loss computation (without loading heavy model)
        batch = {
            "input_ids": torch.randint(0, 100, (2, 16)),
            "labels": torch.randint(0, 100, (2, 16)),
            "diff_mask": torch.randint(0, 2, (2, 16))
        }
        
        loss_weights = {
            "conditional_lm": 1.0,
            "contrastive": 0.5,
            "kl_divergence": 0.1
        }
        
        losses = model.compute_loss(batch, loss_weights)
        
        assert "lm_loss" in losses
        assert "contrastive_loss" in losses
        assert "kl_loss" in losses
        assert "total_loss" in losses
        print("  ✓ Loss computation working")
        
        # Test trainer config
        config = TrainerConfig(
            dry_run=True,
            amp_enabled=True,
            seed=42
        )
        trainer = Trainer(model, config)
        print("  ✓ Trainer initialization working")
        
        # Test prefix freeze
        assert hasattr(model, 'prefix_module')
        prefix_params = list(model.prefix_module.parameters())
        assert len(prefix_params) > 0
        assert all(p.requires_grad for p in prefix_params)
        print("  ✓ Prefix parameters trainable")
        
    except Exception as e:
        print(f"  ✗ Training error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def main():
    print("=" * 60)
    print("SVEN Priority 0, 1, 2 Validation")
    print("=" * 60)
    
    results = []
    results.append(("Priority 0: Repo stabilization", test_priority_0()))
    results.append(("Priority 1: Data pipeline", test_priority_1()))
    results.append(("Priority 2: Three-loss training", test_priority_2()))
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All priorities validated successfully!")
        print("\nNext steps:")
        print("1. Run unit tests: pytest tests/ -v")
        print("2. Test webapp: python webapp\\app.py")
        print("3. Test training: python train.py --config configs/python.yaml --dry-run")
        return 0
    else:
        print("\n✗ Some validations failed. Check errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
