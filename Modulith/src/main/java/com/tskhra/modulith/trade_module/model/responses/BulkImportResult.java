package com.tskhra.modulith.trade_module.model.responses;

import java.util.List;

public record BulkImportResult(
        int created,
        int skipped,
        int failed,
        List<String> errors
) {}
