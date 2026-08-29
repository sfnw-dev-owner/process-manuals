local dependencyMode = os.getenv("DXF_DEPS") ~= nil -- Set in ./go .

-- Return whether path is missing or an empty file.
local function missingOrEmpty(path)
   local f <close> = io.open(path, "rb")
   return not f or f:seek("end") == 0
end

-- Render a QCAD .dxf file's specified layers to PDF. Return the PDF's
-- absolute and relative paths (annoyingly pandoc wants absolute and
-- typst wants relative).
local function renderDXF(src, layers)
   local f <close> = assert(io.open(src, "rb"))
   local contents = f:read("*a")

   local hash = pandoc.sha1(contents .. "\0" .. src .. "\0" .. layers)
   local basename = src:match("([^/\\]+)$"):gsub("%.[^.]+$", "")
   local renderedDXFs = ".rendered-dxfs"

   local relOutput = string.format("/%s/%s-%s.pdf", renderedDXFs, basename, hash)
   pandoc.system.make_directory("/s/"..renderedDXFs, true)
   local absOutput = string.format("/s/%s/%s-%s.pdf", renderedDXFs, basename, hash)

   if missingOrEmpty(absOutput) then
      local stdout = pandoc.pipe(
         "/opt/qcad/qcad",
         {
            "-platform", "offscreen",
            "-no-gui",
            "-allow-multiple-instances",
            "-autostart", "/s/render/dxf-export.js",
            "-f",
            "-o", absOutput,
            "--clipart=/s/common/clipart",
            "--layers=" .. layers,
            src,
         },
         ""
      )
      if os.getenv("DEBUG") ~= nil then print("QCAD STDOUT: " .. stdout) end
   end

   return absOutput, relOutput
end

-- Force Typst to consider the .dxf a dependency without using
-- it as an image source (which it doesn't know how to do).
local function dxfDependency(src)
   return pandoc.RawInline("typst", string.format("#let _ = read(%q, encoding: none)\n", src))
end

-- Handle ![](path/to.dxf){layers=0,1,2} style images.
function Image(el)
   local src = el.src
   if not src:match("%.dxf$") then
      return nil
   end

   if dependencyMode then
      return dxfDependency(src)
   end

   el.src = renderDXF(src, el.attributes.layers)
   el.attributes['layers'] = nil

   return el
end


-- Handle `#fullscreen("path/to.dxf", layers:"0,1,2")`{=typst} style images.
function RawInline(el)
   if FORMAT ~= "typst" or el.format ~= "typst" then
      return nil
   end

   local src, _, layers = el.text:match('"([^"]+%.dxf)"(.-)layers%s*:%s*"([^"]*)"')

   if not src then
      return nil
   end

   if dependencyMode then
      return dxfDependency(src)
   end

   local _, relativePath = renderDXF(src, layers)

   el.text = el.text:gsub(
      '"' .. src:gsub("([^%w])", "%%%1") .. '"',
      string.format("%q", relativePath),
      1
   )
   el.text = el.text:gsub(", *layers:.*", "", 1) .. ")"
   return el
end
