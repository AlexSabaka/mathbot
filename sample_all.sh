# mkdir -p output_png_k1
mkdir -p output_grading_k1

for f in $( ls ./src/templates/**/k1_*.yaml ); do
    out_file="output_grading_k1/$(basename "$f" .yaml).json"
    uv run mathbot grade $f --model qwen3.5:9b --rubric all --strict --json >> $out_file
    # DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib uv run mathbot generate --input $f -o png --file $out_file
done