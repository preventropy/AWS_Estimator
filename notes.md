# UPDATES

### Pricing from AWS
1. Download the pricing data direct from AWS. It's served as a .json from a GET request [here](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/us-west-2/index.json)
2. Move the json file from /Downloads to /Git/AWS_VM_Pricing_Calculator
3. Run `run_pricing_update.bat`

### Add New Instance Types 
1. Edit `index.html`
    - Add instance type to the `const RATES` array
    - Add instance type to the dorpdown as a new `option value= ""`
2. Edit `update_pricing.py` around line 30
    - Add to `INSTANCES = ["t3a.large", "t3a.xlarge", "m5.xlarge", "g4ad.xlarge"]`
    - Add to `r"(t3a\.large|t3a\.xlarge|m5\.xlarge|g4ad\.xlarge) Instance Hour"`

# NOTE: EBS pricing is still 100% manual

# TO DOs
- include EBS in the pricing update process