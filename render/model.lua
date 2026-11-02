-- Figures drawn from the model: a manual embeds one as
-- ![](model:<manual>/<figure>@1:<N>) or, in raw typst, as "model:<manual>/<figure>@1:<N>"
-- where an image path goes, e.g. `#fullpage("model:platform/step_03@1:20")`{=typst}
-- (a drawing is printed at 1:N; a page of 3D views has its own size and takes no scale).
-- render/model2svg.py renders each to SVG (cached in .rendered-figures/) and
-- this filter points the manual at it.
-- Values from the model: a manual writes {{STUD_LENGTH}} where it states a
-- dimension, and this filter replaces it with the value's text from
-- render/values.py (84”: the unit comes from the model).

local dependencyMode = os.getenv("MODEL_DEPS") ~= nil -- Set in ./go.

local PATTERN = "model:[%w_%-]+/[%w_%-%.]+[@%d:%.]*"

-- The figures an element refers to.
local function refs(el)
   local found = {}
   if el.t == "Image" then
      if el.src:match("^" .. PATTERN .. "$") then
         table.insert(found, el.src)
      end
   elseif (el.t == "RawInline" or el.t == "RawBlock") and el.format == "typst" then
      for ref in el.text:gmatch('"(' .. PATTERN .. ')"') do
         table.insert(found, ref)
      end
   end
   return found
end

-- Ask model2svg.py (once per document) for the figures' SVGs, rendering any
-- that aren't cached. {ref: {svg = "/.rendered-figures/...", deps = {...}}}
local function resolve(doc)
   local wanted, seen = {}, {}
   local function collect(el)
      for _, ref in ipairs(refs(el)) do
         if not seen[ref] then
            seen[ref] = true
            table.insert(wanted, ref:sub(#"model:" + 1))
         end
      end
   end
   doc:walk({ Image = collect, RawInline = collect, RawBlock = collect })
   if #wanted == 0 then
      return {}
   end
   local args = { "/s/render/model2svg.py" }
   if dependencyMode then
      table.insert(args, "--deps")
   end
   for _, figure in ipairs(wanted) do
      table.insert(args, figure)
   end
   return pandoc.json.decode(pandoc.pipe("python3", args, ""), false)
end

-- Force Typst to consider a figure's sources dependencies (for the
-- last-revision date in ./go) without reading its SVG, which the dependency
-- pass doesn't render.
local emitted = {} -- each dependency once per document
local function dependencies(figures, found)
   local reads = {}
   for _, ref in ipairs(found) do
      for _, dep in ipairs(figures[ref:sub(#"model:" + 1)].deps) do
         if not emitted[dep] then
            emitted[dep] = true
            table.insert(reads, string.format("#let _ = read(%q, encoding: none)", dep))
         end
      end
   end
   return table.concat(reads, "\n") .. "\n"
end

-- Ask values.py (once per document) for the text of the {{values}} the
-- document's Str elements hold: {values = {expr = text}, deps = {...}}
local VALUE = "{{([^{}]+)}}"
local function values(doc)
   local wanted, seen = {}, {}
   doc:walk({ Str = function(el)
      for expr in el.text:gmatch(VALUE) do
         if not seen[expr] then
            seen[expr] = true
            table.insert(wanted, expr)
         end
      end
   end })
   if #wanted == 0 then
      return { values = {}, deps = {} }
   end
   local args = { "/s/render/values.py" }
   if dependencyMode then
      table.insert(args, "--deps")
   end
   for _, expr in ipairs(wanted) do
      table.insert(args, expr)
   end
   return pandoc.json.decode(pandoc.pipe("python3", args, ""), false)
end

function Pandoc(doc)
   if FORMAT ~= "typst" then
      return nil
   end
   local figures = resolve(doc)
   local vals = values(doc)

   local function str(el)
      if not el.text:find("{{", 1, true) then
         return nil
      end
      return pandoc.Str((el.text:gsub(VALUE, function(expr) return vals.values[expr] end)))
   end

   local function image(el)
      local found = refs(el)
      if #found == 0 then
         return nil
      end
      if dependencyMode then
         return pandoc.RawInline("typst", dependencies(figures, found))
      end
      el.src = "/s" .. figures[el.src:sub(#"model:" + 1)].svg
      return el
   end

   local function raw(el)
      local found = refs(el)
      if #found == 0 then
         return nil
      end
      if dependencyMode then
         el.text = dependencies(figures, found)
         return el
      end
      for _, ref in ipairs(found) do
         el.text = el.text:gsub('"' .. ref:gsub("%p", "%%%0") .. '"',
                                string.format("%q", figures[ref:sub(#"model:" + 1)].svg))
      end
      return el
   end

   doc = doc:walk({ Str = str, Image = image, RawInline = raw, RawBlock = raw })
   if dependencyMode and #vals.deps > 0 then
      -- The values' modules are dependencies too (see dependencies() above).
      local reads = {}
      for _, dep in ipairs(vals.deps) do
         table.insert(reads, string.format("#let _ = read(%q, encoding: none)", dep))
      end
      doc.blocks:insert(pandoc.RawBlock("typst", table.concat(reads, "\n")))
   end
   return doc
end
