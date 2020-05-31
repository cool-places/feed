from app_state import cursor, block_size
import time

class Stream:
    def __init__(self, locality):
        self.locality = locality
        # unbounded cache...good enough for testing purposes
        # but not for production
        self.cache = dict()

        now = int(time.time())
        self.tip = now - now % block_size

        # order from new to old (DESC)
        cursor.execute('SELECT creator, creationTime, likes, seenBy\
                FROM Posts\
                WHERE locality=?\
                AND creationTime BETWEEN ? AND ?\
                ORDER BY creationTime DESC', locality, self.tip, self.tip + block_size - 1)

        self.cache[self.tip] = cursor.fetchall() 

    def update_tip(self):
        cursor.execute('SELECT creator, creationTime, likes, seenBy\
                FROM Posts\
                WHERE locality=?\
                AND creationTime BETWEEN ? AND ?\
                ORDER BY creationTime DESC', self.locality, self.tip, self.tip + block_size - 1)
        self.cache[self.tip] = cursor.fetchall()
        
        now = int(time.time())
        new_tip = now - now % block_size

        if new_tip != self.tip:
            self.tip = new_tip
            cursor.execute('SELECT creator, creationTime, likes, seenBy\
                FROM Posts\
                WHERE locality=?\
                AND creationTime BETWEEN ? AND ?\
                ORDER BY creationTime DESC', self.locality, self.tip, self.tip + block_size - 1)
            self.cache[self.tip] = cursor.fetchall()
            

    def get_tip(self):
        return self.cache[self.tip]

    def get_block(self, ts):
        assert(ts % self.block_size == 0)

        if ts in self.cache:
            return self.cache[ts]
        
        cursor.execute('SELECT creator, creationTime, likes, seenBy\
            FROM Posts\
            WHERE locality=?\
            AND creationTime BETWEEN ? AND ?\
            ORDER BY creationTime DESC', locality, ts, ts + block_size - 1)
        self.cache[ts] = cursor.fetchall()
        return self.cache[ts]
        




    
