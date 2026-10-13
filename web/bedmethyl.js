/* Pure browser/Node parser for modkit pileup bedMethyl (18 columns).
 * Count aggregation is stratified by modification code to avoid double counting.
 */
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.BedMethyl = api;
})(typeof window === "undefined" ? null : window, function () {
  "use strict";
  const MAX_BYTES = 20 * 1024 * 1024;

  function csvCell(value) {
    const raw = String(value);
    const safe = /^[\s]*[=+@-]/.test(raw) ? "'" + raw : raw;
    return '"' + safe.replace(/"/g, '""') + '"';
  }

  function parse(text, options = {}) {
    if (typeof text !== "string" || text.length > MAX_BYTES) {
      throw new Error("Choose a UTF-8 text file smaller than 20 MiB.");
    }
    const minimum = Number(options.minimumCoverage ?? 1);
    const code = options.modification ?? "m";
    if (!Number.isSafeInteger(minimum) || minimum < 1 || minimum > 1000000) {
      throw new Error("Minimum valid coverage must be an integer from 1 to 1,000,000.");
    }
    if (!["m", "h", "all"].includes(code)) {
      throw new Error("Unknown modification filter.");
    }
    const groups = new Map();
    const warnings = [];
    let parsed = 0, malformed = 0, filtered = 0, accepted = 0;
    const lines = text.split(/\r?\n/);
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line || line.startsWith("#") || line.startsWith("track ") || line.startsWith("browser ")) continue;
      const c = line.split("\t");
      if (c.length < 18) {
        malformed++;
        if (warnings.length < 5) warnings.push("Line " + (i + 1) + ": expected 18 tab-separated bedMethyl columns.");
        continue;
      }
      const integer = (x) => /^\d+$/.test(x) && Number.isSafeInteger(Number(x)) ? Number(x) : NaN;
      const start = integer(c[1]), end = integer(c[2]);
      const coverage = integer(c[9]), modified = integer(c[11]);
      const canonical = integer(c[12]), other = integer(c[13]);
      const mod = c[3].split(",")[0];
      const percentage = Number(c[10]);
      if (!c[0] || !(end > start) ||
          ![coverage, modified, canonical, other].every(Number.isSafeInteger) ||
          coverage === 0 || modified + canonical + other !== coverage ||
          !Number.isFinite(percentage) || percentage < 0 || percentage > 100 ||
          Math.abs(percentage - 100 * modified / coverage) > 0.15) {
        malformed++;
        if (warnings.length < 5) warnings.push("Line " + (i + 1) + ": inconsistent coordinate, count, or percentage.");
        continue;
      }
      parsed++;
      if ((code !== "all" && code !== mod) || coverage < minimum) {
        filtered++;
        continue;
      }
      const key = JSON.stringify([c[0], mod]);
      const group = groups.get(key) || {
        chromosome: c[0], modification: mod, sites: 0,
        validCoverage: 0, modifiedCalls: 0
      };
      group.sites++;
      group.validCoverage += coverage;
      group.modifiedCalls += modified;
      groups.set(key, group);
      accepted++;
    }
    const summary = Array.from(groups.values())
      .map(g => ({ ...g, percentModified: 100 * g.modifiedCalls / g.validCoverage }))
      .sort((a, b) => a.chromosome.localeCompare(b.chromosome, undefined, {numeric:true})
        || a.modification.localeCompare(b.modification));
    return { summary, parsed, malformed, filtered, accepted, warnings };
  }

  function toCSV(summary) {
    const columns = ["chromosome", "modification", "sites", "valid_coverage",
      "modified_calls", "percent_modified"];
    const lines = [columns.join(",")];
    for (const r of summary) {
      lines.push([r.chromosome, r.modification, r.sites, r.validCoverage,
        r.modifiedCalls, r.percentModified.toFixed(4)].map(csvCell).join(","));
    }
    return lines.join("\r\n") + "\r\n";
  }
  return { parse, toCSV, csvCell };
});
