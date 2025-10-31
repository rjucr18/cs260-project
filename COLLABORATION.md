# Collaboration Guide: Avoiding Merge Conflicts

This guide helps Rohit and Kush work independently on separate branches while minimizing merge conflicts.

## 🗂️ File Ownership

### Rohit Owns (Partner 1):
```
prefix_tuning/        # All files - implement SecurePrefixTuning
models/               # All files - CodeGen wrappers (EXCEPT interfaces.py)
training/             # All files - training loop, loss functions
configs/training.yaml # Training hyperparameters
requirements/training.txt
Dockerfile           # Update if training needs change
```

### Kush Owns (Partner 2):
```
data/                 # All files - dataset loaders (EXCEPT schemas.py, interfaces.py)
evaluation/           # All files - CodeQL, HumanEval (EXCEPT interfaces.py)
webapp/               # All files - Flask demo
configs/evaluation.yaml
requirements/evaluation.txt
```

### Shared Files (⚠️ Coordinate Before Modifying):
```
data/schemas.py       # Data structures - discuss changes in team meeting
data/interfaces.py    # Dataset API contract
models/interfaces.py  # Model API contract
evaluation/interfaces.py  # Evaluation API contract
requirements/base.txt # Only add if BOTH need the dependency
README.md            # Coordinate updates
docker-compose.yml   # Coordinate service changes
```

## 📅 Weekly Workflow

### Week 1 (Current): Independent Development ✅
**Status:** SAFE - No conflicts expected

**Rohit:**
- Work on `rohit-model-prefix-docker` branch
- Implement prefix-tuning skeleton
- Load CodeGen models
- Set up Docker for training
- No need to merge yet

**Kush:**
- Work on `kush-data-codeql-webapp` branch
- Download and clean datasets
- Install CodeQL
- Create Flask app skeleton
- No need to merge yet

**End of Week 1:** Quick sync meeting (15 minutes)
- Verify data schema works for both
- Verify model interface works for both
- No merge required if schemas are good

### Week 2: First Integration
**Status:** MODERATE RISK - Plan carefully

**Monday (Start of Week 2):**
1. Both: Pull latest master
   ```bash
   git checkout master
   git pull origin master
   ```

2. Both: Merge master into your branch
   ```bash
   git checkout rohit-model-prefix-docker  # or kush-data-codeql-webapp
   git merge master
   ```

**During Week 2:**
- Rohit: Implement actual training loop that calls `DatasetLoader.load()`
- Kush: Implement actual dataset loaders that return `VulnerabilityPair` objects
- Test integration locally:
  ```python
  # Kush's data loader should work with Rohit's training code
  from data.big_vul import BigVulDataset
  from training.train import Trainer
  
  dataset = BigVulDataset()
  trainer = Trainer(dataset)
  trainer.train()  # Should work without modifications!
  ```

**Friday (End of Week 2):** Integration Day
1. Rohit merges his branch to master:
   ```bash
   git checkout master
   git merge rohit-model-prefix-docker
   git push origin master
   ```

2. Kush merges his branch to master (after Rohit):
   ```bash
   git checkout master
   git pull origin master  # Get Rohit's changes
   git merge kush-data-codeql-webapp
   # Resolve any conflicts (should be minimal if interfaces were followed)
   git push origin master
   ```

3. Both: Test end-to-end pipeline together

### Week 3: Parallel Feature Development
**Status:** HIGHER RISK - Use feature branches

**Switch to feature branches** (cleaner than long-lived personal branches):
```bash
# Rohit creates feature branches:
git checkout master
git pull origin master
git checkout -b feature/hyperparameter-tuning
# ... work ...
git checkout master
git merge feature/hyperparameter-tuning
git push origin master

# Kush creates feature branches:
git checkout master
git pull origin master
git checkout -b feature/codeql-integration
# ... work ...
git checkout master
git merge feature/codeql-integration
git push origin master
```

**Merge Strategy:**
- Merge small features frequently (every 1-2 days)
- Don't let branches diverge >3 days from master
- Always pull master before merging your feature

### Week 4: Final Integration & Demo
**Status:** CRITICAL - Coordinate closely

**Daily standups** (5 minutes):
- What did you merge yesterday?
- What will you merge today?
- Any blockers?

**Test Pipeline Daily:**
```bash
# Run full end-to-end test
python scripts/test_pipeline.py

# Expected flow:
# 1. Load dataset (Kush's code)
# 2. Train model (Rohit's code)
# 3. Generate code (Rohit's code)
# 4. Evaluate with CodeQL (Kush's code)
# 5. Display in webapp (Kush's code)
```

## 🚨 Conflict Prevention Rules

### Rule 1: One Owner Per File
- If you own a file, you can modify it freely
- If you DON'T own a file, ask first in team chat

### Rule 2: Interfaces Are Sacred
- Never change function signatures in `**/interfaces.py` without discussion
- Add new methods? Fine. Change existing? Team meeting first.

### Rule 3: Config Files Are Separated
- Rohit: Only edit `configs/training.yaml`
- Kush: Only edit `configs/evaluation.yaml`
- Need shared config? Discuss and add to both files identically

### Rule 4: Requirements Are Separated
- Rohit: Only edit `requirements/training.txt`
- Kush: Only edit `requirements/evaluation.txt`
- Need shared dependency? Add to `requirements/base.txt` after discussion

### Rule 5: Test Before Merging
```bash
# Before merging to master, run:
pytest tests/                          # Unit tests pass
python scripts/test_integration.py    # Integration test passes
black . --check                        # Code formatted
flake8 .                              # No linting errors
```

## 🔧 Handling Conflicts When They Happen

If you get a merge conflict:

### Step 1: Don't Panic
Conflicts are normal and fixable!

### Step 2: Identify the Conflict
```bash
git status  # Shows conflicted files
```

### Step 3: Resolve Based on File Type

**For code files:**
```python
<<<<<<< HEAD (your changes)
def my_function():
    return "Rohit's version"
=======
def my_function():
    return "Kush's version"
>>>>>>> feature-branch
```
**Resolution:** Talk to your partner! Probably both changes are needed.

**For config files:**
Usually keep both sections:
```yaml
# Rohit's training config
model:
  learning_rate: 1e-4

# Kush's evaluation config  
evaluation:
  num_samples: 1000
```

**For requirements files:**
Keep both dependencies:
```txt
# Rohit added:
torch>=2.0.0

# Kush added:
flask>=2.3.0

# Keep both!
```

### Step 4: Test After Resolving
```bash
# Mark conflict as resolved
git add <conflicted-file>

# Test that everything works
pytest tests/

# Commit the merge
git commit -m "Merge feature-branch, resolved conflicts in <files>"
```

## 📞 Communication Channels

**Daily (async):**
- Slack/Discord: Quick questions, status updates

**Weekly (sync):**
- Monday: Plan week's work, coordinate on shared files
- Friday: Integration day, merge branches, test together

**As Needed:**
- Before modifying interface files
- Before modifying shared configs
- When stuck on integration issues

## 🎯 Success Metrics

You're doing well if:
- ✅ Merges take <30 minutes
- ✅ <5 conflicted files per merge
- ✅ All tests pass after merge
- ✅ No "emergency" debugging sessions at 2am

You need to improve if:
- ❌ Merges take >2 hours
- ❌ Conflicts in interface files
- ❌ Code breaks after merge
- ❌ One partner blocks the other

## 🆘 Emergency Contact

If you're completely stuck:
1. Create a new branch from master (fresh start)
2. Cherry-pick your changes: `git cherry-pick <commit-hash>`
3. Ask for help in team meeting

---

**Remember:** Interfaces prevent conflicts. Test often. Communicate early.
