# UPDATES
- Add Tsurugi to the OS EC2 options.
- streamline real planning mode, where Jason just cites number of user weeks by each desktop, and it automagically handles the storage being charged by the month (such as rounding up to the nearest multiple of 4)

### Pricing from AWS
1. Download the pricing data direct from AWS. It's served as a .json from a GET request [here](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/us-west-2/index.json)
2. Move the json file from /Downloads to /Git/AWS_VM_Pricing_Calculator
3. Run `run_pricing_update.bat`

### Add New Instance Types 
1. Edit `rates.js`
    - Add instance type to the `const RATES` table (all prices live in `rates.js`)
2. Edit `index.html`
    - Add instance type to the dropdown as a new `option value= ""`
3. Edit `update_pricing.py` around line 30
    - Add to `INSTANCES = ["t3a.large", "t3a.xlarge", "m5.xlarge", "g4ad.xlarge"]`
    - Add to `r"(t3a\.large|t3a\.xlarge|m5\.xlarge|g4ad\.xlarge) Instance Hour"`

# NOTE: EBS pricing is still 100% manual

# TO DOs
- include EBS in the pricing update process via json 
- make Skald pricing more dynamic