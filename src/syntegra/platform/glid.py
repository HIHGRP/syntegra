"""National Global Learner ID allocator (decision CD-07).

Every state registry leases blocks of serials from one national sequence, so a GLID is unique across the country
without the states coordinating. A state leases its first block when it is provisioned and the next one whenever
the current blocks run out.
"""

from __future__ import annotations

import uuid

from django.db import transaction

from syntegra.core.fields import utcnow
from syntegra.platform.models import GlidBlock

BLOCK = 10_000
ALIAS = "platform"


def lease_block(tenant_id: uuid.UUID, size: int = BLOCK) -> GlidBlock:
    """Lease the next free block of ``size`` serials (rounded up to whole blocks) to a state registry."""
    size = max(BLOCK, -(-size // BLOCK) * BLOCK)
    with transaction.atomic(using=ALIAS):
        last = (
            GlidBlock.objects.using(ALIAS)
            .select_for_update()
            .order_by("-last_serial")
            .values_list("last_serial", flat=True)
            .first()
        )
        first = (last or 0) + 1
        block = GlidBlock(tenant_id=tenant_id, first_serial=first, last_serial=first + size - 1, leased_at=utcnow())
        block.save(using=ALIAS)
        return block
