FROM ollama/ollama:latest

# 💡 Sensible defaults for low-RAM laptops
ENV OLLAMA_NUM_PARALLEL=1 \
    OLLAMA_KV_CACHE_TYPE=q4_0 \
    OLLAMA_ORIGINS=*

# Expose the Ollama HTTP API
EXPOSE 11434

# Default command: start the server
CMD ["serve"]