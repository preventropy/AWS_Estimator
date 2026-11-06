/* ═══════════════════════════════════════════════════════════════════
   rates.js: the single source of truth for every price on the site.
   Loaded by each calculator page with <script src="rates.js">.

   RATES is rewritten automatically by update_pricing.py. Keep each
   RATES line in the form   'type': { windows: 0.123, linux: 0.456 },
   or the script won't be able to find it.
   ═══════════════════════════════════════════════════════════════════ */

/* ── General ─────────────────────────────────────────────────────── */
const TAX             = 0.09;   // applied to every line
const WEEKS_PER_MONTH = 4;

/* ── EC2 on-demand, $/hr, us-west-2 (auto-updated) ───────────────── */
const RATES = {
  't3a.large':  { windows: 0.1028,   linux: 0.0752  },
  't3a.xlarge': { windows: 0.224,    linux: 0.1504  },
  'm5.xlarge':  { windows: 0.376,    linux: 0.192   },
  'g4ad.xlarge':{ windows: 0.56253,  linux: 0.37853 },
  'g4dn.xlarge':{ windows: 0.71,     linux: 0.526   },
};

/* ── EC2 with SQL Server Web licensing, $/hr (updated by hand) ───── */
const SQL_WEB_RATES = {
  't3a.medium': { windowsSqlWeb: 0.1236 },
  't3a.xlarge': { windowsSqlWeb: 0.2916 },
  'm6a.xlarge': { windowsSqlWeb: 0.4244, linuxSqlWeb: 0.2404 },
};

/* ── Add-ons ─────────────────────────────────────────────────────── */
const MARKETPLACE_UBUNTU_RATE = 0.05;  // $/hr on top of Linux

/* ── EBS storage, $/GB-month (updated by hand) ───────────────────── */
const EBS_GP2_RATE = 0.10;
const EBS_GP3_RATE = 0.08;

/* ── Desktops (40 hr work week) ──────────────────────────────────── */
const EC2_HOURS  = 40;
const LB_WEEKLY  = 0.35;   // load-balancing, per user per week
const BW_WEEKLY  = 0.40;   // bandwidth, per user per week

/* ── Skald servers (run 24/7) ────────────────────────────────────── */
const SKALD_HOURS            = 168;
const SKALD_BANDWIDTH_WEEKLY = 10.00;

// platform: 'windows' | 'linux' (from RATES) or 'windowsSqlWeb' | 'linuxSqlWeb' (from SQL_WEB_RATES)
// gp2 / gp3: GB of storage
const SKALD_SYSTEMS = {
  ChirpyHub:  { name: 'ChirpyHub',   instance: 't3a.xlarge', platform: 'windowsSqlWeb', gp2: 100, gp3: 1122 },
  SocialPark: { name: 'SocialPark',  instance: 'm6a.xlarge', platform: 'windowsSqlWeb', gp2: 140, gp3: 602  },
  CareerHub:  { name: 'CareerHub',   instance: 't3a.xlarge', platform: 'windowsSqlWeb', gp2: 120, gp3: 510  },
  InfoLink:   { name: 'InfoLink',    instance: 't3a.medium', platform: 'windowsSqlWeb', gp2: 0,   gp3: 139  },
  CAPost:     { name: 'CAPost',      instance: 't3a.large',  platform: 'windows',       gp2: 0,   gp3: 100  },
  VideoHub:   { name: 'VideoHub',    instance: 't3a.medium', platform: 'windowsSqlWeb', gp2: 0,   gp3: 174  },
  ArgusForge: { name: 'Argus Forge', instance: 'm6a.xlarge', platform: 'linuxSqlWeb',   gp2: 0,   gp3: 250  },
};

/* ═══════════ Helpers (no prices below this line) ═══════════ */

// Hourly rate for an instance + platform, looked up in RATES or SQL_WEB_RATES.
function hourlyRate(instance, platform) {
  const table = platform.endsWith('SqlWeb') ? SQL_WEB_RATES : RATES;
  const rate  = table[instance] && table[instance][platform];
  if (rate === undefined) throw new Error(`rates.js: no ${platform} rate for ${instance}`);
  return rate;
}

// Weekly cost of storage billed monthly (monthly price ÷ 4 weeks), before tax.
function weeklyStorage(gp2, gp3) {
  return (gp2 * EBS_GP2_RATE + gp3 * EBS_GP3_RATE) / WEEKS_PER_MONTH;
}

// Skald weekly price: 24/7 compute + bandwidth + storage, plus tax, rounded UP to the whole dollar.
function skaldWeeklyPrice(sys) {
  const pretax = hourlyRate(sys.instance, sys.platform) * SKALD_HOURS
               + SKALD_BANDWIDTH_WEEKLY
               + weeklyStorage(sys.gp2, sys.gp3);
  return Math.ceil(pretax * (1 + TAX));
}

// { key: { label, price } }, built from SKALD_SYSTEMS (the shape the Old page's Skald section uses).
const SKALD_RATES = Object.fromEntries(
  Object.entries(SKALD_SYSTEMS).map(([key, sys]) => [
    key,
    { label: `${sys.name} (${sys.instance})`, price: skaldWeeklyPrice(sys) },
  ])
);
