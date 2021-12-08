-- upgrade --
ALTER TABLE "user" ADD "subscribed" INT NOT NULL  DEFAULT 1;
-- downgrade --
ALTER TABLE "user" DROP COLUMN "subscribed";
