# 🐛 Utilities Bug Fix Summary

## Problem Identified

**User Reported Issues:**
1. **Rates (Council Tax)** - No usage/metering, just a fixed cost
2. **Gas (45kg Cylinders)** - Should be measured in "bottles", not kWh
3. **Form requires usage field** - Can't enter rates without a usage value

## Root Cause

The utilities data model was designed for metered utilities only:
- `usage` and `cost_per_unit` were required (NOT NULL)
- Frontend validation forced usage > 0
- No support for fixed-cost utilities like council rates

---

## ✅ Backend Fixes Applied

### 1. Database Model Updated (`app/models/utility.py`)
- ✅ `usage` → Nullable (can be None for rates)
- ✅ `unit` → Nullable (can be None for rates)
- ✅ `cost_per_unit` → Nullable (None when no usage)
- ✅ Updated `to_dict()` to handle None values

### 2. Schema Updated (`app/schemas/utility.py`)
- ✅ `UtilityCreate.usage` → Optional[Decimal]
- ✅ `UtilityCreate.unit` → Optional[str]
- ✅ `UtilityResponse` → All nullable fields marked Optional[float]

### 3. Service Logic Updated (`app/services/utility_service.py`)
- ✅ `create_utility()` - Calculates cost_per_unit only if usage provided
- ✅ `update_utility()` - Handles None usage gracefully
- ✅ Validation - Usage > 0 check only if usage is not None

### 4. Database Migration Created
- ✅ `fix_utilities_nullable_usage.py` - Makes columns nullable
- **Run on Pi:** `docker compose -f docker-compose.pi.yml exec backend alembic upgrade head`

---

## ⚠️ Frontend Fixes Needed (Not Yet Applied)

The frontend still needs these updates:

### File: `frontend/src/pages/Financial/UtilitiesTab.tsx`

**Issue 1: Line 95 - Null reference error**
```typescript
// CURRENT (BREAKS):
setFormUsage(utility.usage.toString());

// FIX:
setFormUsage(utility.usage !== null ? utility.usage.toString() : '');
```

**Issue 2: Line 96 - Null reference error**
```typescript
// CURRENT (BREAKS):
setFormUnit(utility.unit);

// FIX:
setFormUnit(utility.unit || '');
```

**Issue 3: Lines 127-142 - Validation too strict**
```typescript
// CURRENT (BREAKS FOR RATES):
if (!formProvider || !formPeriodStart || !formPeriodEnd || !formUsage || !formUnit || !formCost) {
  toast.error('Please fill in all required fields');
  return;
}

// FIX:
const isFixedCost = formType === 'rates';  // Rates don't have usage

if (!formProvider || !formPeriodStart || !formPeriodEnd || !formCost) {
  toast.error('Please fill in all required fields');
  return;
}

if (!isFixedCost && (!formUsage || !formUnit)) {
  toast.error('Please enter usage and unit for metered utilities');
  return;
}
```

**Issue 4: Line 137-142 - Usage validation**
```typescript
// CURRENT (BREAKS FOR RATES):
const usage = parseFloat(formUsage);
const cost = parseFloat(formCost);
if (isNaN(usage) || usage <= 0 || isNaN(cost) || cost <= 0) {
  toast.error('Usage and cost must be greater than 0');
  return;
}

// FIX:
const cost = parseFloat(formCost);
if (isNaN(cost) || cost <= 0) {
  toast.error('Cost must be greater than 0');
  return;
}

const usage = formUsage ? parseFloat(formUsage) : null;
if (usage !== null && (isNaN(usage) || usage <= 0)) {
  toast.error('Usage must be greater than 0');
  return;
}
```

**Issue 5: Submit payload - Send null for rates**
```typescript
// IN CREATE/UPDATE CALLS:
const payload = {
  utility_type: formType,
  provider: formProvider,
  billing_period_start: format(formPeriodStart, 'yyyy-MM-dd'),
  billing_period_end: format(formPeriodEnd, 'yyyy-MM-dd'),
  usage: formUsage ? parseFloat(formUsage) : null,  // null for rates
  unit: formUnit || null,  // null for rates
  cost: parseFloat(formCost),
  notes: formNotes || undefined
};
```

**Issue 6: UI - Show/hide usage fields**
Add conditional rendering in the form JSX:
```tsx
{formType !== 'rates' && (
  <>
    <div className="space-y-2">
      <Label htmlFor="usage">Usage *</Label>
      <Input
        id="usage"
        type="number"
        step="0.01"
        value={formUsage}
        onChange={(e) => setFormUsage(e.target.value)}
        placeholder={formType === 'gas' ? 'Number of bottles' : 'Usage amount'}
      />
    </div>

    <div className="space-y-2">
      <Label htmlFor="unit">Unit *</Label>
      <Input
        id="unit"
        type="text"
        value={formUnit}
        onChange={(e) => setFormUnit(e.target.value)}
        placeholder={formType === 'gas' ? 'bottles' : 'kWh, m³, GB, etc.'}
      />
    </div>
  </>
)}

{formType === 'rates' && (
  <p className="text-sm text-gray-500 italic">
    Council rates are a fixed cost with no usage metering
  </p>
)}
```

---

## 📋 Deployment Steps

### Step 1: Copy Updated Backend Files to Pi
```bash
# Backend files
backend/app/models/utility.py
backend/app/schemas/utility.py
backend/app/services/utility_service.py
backend/alembic/versions/fix_utilities_nullable_usage.py
```

### Step 2: Run Migration on Pi
```bash
docker compose -f docker-compose.pi.yml exec backend alembic upgrade head
```

### Step 3: Restart Backend (if needed)
```bash
docker compose -f docker-compose.pi.yml restart backend
```

### Step 4: Fix Frontend (Manual)
Apply the frontend fixes documented above to:
- `frontend/src/pages/Financial/UtilitiesTab.tsx`

### Step 5: Rebuild Frontend
```bash
docker compose -f docker-compose.pi.yml up -d --build frontend
```

---

## 🧪 Testing

After deployment, test these scenarios:

1. **Create Rates Entry:**
   - Type: rates
   - Provider: Brisbane City Council
   - Period: 01/01/2026 - 31/03/2026
   - Cost: $587.50
   - Usage/Unit: Leave blank
   - ✅ Should save successfully

2. **Create Gas Entry (Bottles):**
   - Type: gas
   - Provider: Origin Energy
   - Period: 01/02/2026 - 28/02/2026
   - Usage: 2
   - Unit: bottles
   - Cost: $145.00
   - ✅ Should calculate cost per bottle

3. **Create Electricity Entry:**
   - Type: electricity
   - Provider: AGL
   - Period: 01/02/2026 - 28/02/2026
   - Usage: 450
   - Unit: kWh
   - Cost: $187.23
   - ✅ Should calculate cost per kWh

---

## 🎯 Status

- ✅ Backend Model - Fixed
- ✅ Backend Schema - Fixed
- ✅ Backend Service - Fixed
- ✅ Database Migration - Created
- ⚠️ Frontend - Needs manual fixes (documented above)
- ⏳ Testing - Pending deployment

**Estimated Fix Time for Frontend:** 15-20 minutes
